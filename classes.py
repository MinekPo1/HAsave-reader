import logging
# import re
from typing import Literal, Optional, overload
from values import *
from pathlib import Path


specialKeyRegex = [
	r"basket[0-9]+",
	r"chunk\(.*,-?[0-9]+, -?[0-9]+\)",
	r"NPCchest_[0-9]+",
	r"shack[0-9]+-zonedata",
	r"sign[0-9]+"
]


class HASave:
	__offset__:int = 0

	def __init__(self):
		self.data = bytearray([])
		self.save_version = 0
		self.section_count = 0
		self.values = {}
		self.__offset__ = 0

	def encode(
		self,version:int | None = None,sections:int | None = None,
		data:dict | None = None
	) -> bytearray:
		if version is None:
			version = self.save_version
		if sections is None:
			sections = self.section_count
		if data is None:
			data = self.values

		ba = bytearray()
		logging.info("serilising")
		logging.info(data)
		logging.debug("(HASave.encode) writing version to bytearray")
		ba.insert(0, version % 255)
		logging.debug("(HASave.encode) inserting section count")
		self.__insert_short__(ba,sections)
		for key, value in data.items():
			if key is None:
				raise ValueError("Key is None")
			if value is None:
				raise ValueError(f"Value for key: {key} is None")
			self.__insert_str__(ba,key)
			logging.debug(f"(HASave.encode) inserting key: {key}")
			datatype = resolve_type(key)
			if datatype == "short":
				self.__insert_short__(ba,value)
			if datatype == "long":
				self.__insert_long__(ba,value)
			if datatype == "str":
				self.__insert_str__(ba, value)
			if datatype is None:
				raise ValueError(f"Key: {key!r} has no type associated")
		return ba

	def decode(self, ba:bytearray):
		self.data = ba
		self.save_version = self.__pop_byte__()
		self.section_count = self.__extract_short__()
		while True:
			key, var = self.__extract_auto__()
			if key == "long":
				logging.error("key is long!")
			if key is None:
				if var == "EOF":
					break
				continue
			if var is None:
				raise NameError(f"Parse Error @ Offset: {self.__offset__} {key}")
			logging.debug(f"(HASave.decode) {key}: {var}")
			# if self.section_count >= 2:
			# 	superKey = None
			# 	for regex in specialKeyRegex:
			# 		if re.search(regex,key):
			# 			superKey = key
			# 	if superKey is None:
			# 		self.values[key] = var
			# 	if superKey not in self.values.keys():
			# 		self.values[superKey] = {}
			# 	self.values[superKey][key] = var
			# else:
			self.values[key] = var

	def __pop_byte__(self)->int:
		self.__offset__ += 1
		return self.data[self.__offset__-1]

	def __get_hex__value__(self) -> str:
		# sourcery skip: use-fstring-for-concatenation
		return ("0" + hex(self.__pop_byte__())[2:])[-2:]
		# this looks bad, but its the fastest way.
		# Also this function is never used anyway.

	def __extract_auto__(self,signed=True)\
			-> tuple[str,int | str] | tuple[Optional[str],None | Literal["EOF"]]:
		try:
			key, lenght = self.__extract_str__()
		except IndexError:
			return None, "EOF"
		logging.debug(f"(HASave.__extract_auto__) read key: {key}, len: {lenght}")
		if lenght in [0, 1] or len(key) == 0:
			return None, None
		var_type = resolve_type(key)
		if var_type == "short":
			return key, self.__extract_short__(signed)
		if var_type == "long":
			return key, self.__extract_long__(signed)
		if var_type == "str":
			return key, self.__extract_str__()[0]
		if var_type is None:
			logging.error(f"Key: {key!r} has no type associated")
		else:
			logging.error(f"Unknown type: {var_type!r}")
		return key, None

	def __extract_short__(self,signed:bool = True,requireLowNonZero:bool = False)\
			-> int:
		lh = self.__pop_byte__()
		if (lh == 0) and requireLowNonZero:
			return 0
		hh = self.__pop_byte__()
		return hh*256+lh

	def __extract_long__(self,signed=True) -> int:
		# TODO: implement non signed longs
		if not(signed):
			raise NotImplementedError("Unsigned longs are not implemented")
		return sum(self.__pop_byte__() * 256 ** i for i in range(4))

	def __extract_str__(self) -> tuple[str, int]:
		str_len = self.__extract_short__(signed=False,requireLowNonZero=True)
		if str_len == 0:
			logging.debug("(HASave.__extract_str__) zero-length string")
			return "",0
		if str_len % 2 == 1:
			logging.debug("(HASave.__extract_str__) uneven length string")
			return "",1
		string = ""
		chrv = -1
		try:
			for _ in range(int(str_len/2)):
				chrv = self.__extract_short__(signed=False)
				val = chr(chrv)
				if val == '\x00':
					return "",1
					# maybe this should be interpreted as an early string termination?
				string += val
		except ValueError as ve:
			if chrv != -1:
				logging.debug(f"(HASave.__extract_str__) {chrv} is not a valid char")
			raise ve from ve
		return string,str_len

	def __insert_short__(self,ba:bytearray,value:int):
		logging.debug(f"(HASave.__extract_short__) writing short: {value}")
		if value < 0:
			value += 65536
		if value < 0 or value > 65535:
			raise ValueError("Value must be more then -32769 but less then 32768")

		ba.append(value  % 256)
		ba.append(value // 256)

	def __insert_long__(self,ba:bytearray,value:int):
		logging.debug(f"(HASave.__extract_long__) writing long: {value}")
		val = value
		if val < 0:
			val += 4294967296
		if val < 0 or val > 4294967295:
			raise ValueError(
				"Value must be more then -2147483649 "
				"but less then 2147483648"
			)
		ba.append(val           % 256)
		ba.append(val // 256    % 256)
		ba.append(val // 256**2 % 256)
		ba.append(val // 256**3 % 256)
		# yes I know

	def __insert_str__(self,ba:bytearray,string:str):
		logging.debug(f"(HASave.__insert_str__) writing string: {string}")
		if string is None:
			raise ValueError("String must not be None")
		if len(string) > 125:
			raise ValueError('string must be less then 125 charachters long')
		ba.append(len(string)*2)
		ba.append(0)
		for char in string:
			ba.append(ord(char))
			ba.append(0)

	def __repr__(self):
		return f"<HAsave v:{self.save_version} obj#: {len(self.values)}>"

	def __getitem__(self,key):
		return self.values[key]

	@classmethod
	def from_decode(cls, ba:bytearray):
		ret = cls()
		ret.decode(ba)
		return ret

	@classmethod
	def load(cls,path:str | Path):
		with open(path,'rb') as f:
			return cls.from_decode(bytearray(f.read()))

	def dump(self,path:str | Path):
		with open(path,'wb') as f:
			f.write(self.encode())


class HASlot(object):
	class HASlotValuesView:
		"""
		A view of the values in a slot.
		Should be compatible with a dict-like interface.
		"""
		def __init__(self,slot:'HASlot'):
			self.slot = slot

		def __getitem__(self,key):
			return self.slot.files[key].values

		def __setitem__(self,key,value):
			self.slot.files[key].values = value

		def __delitem__(self,key):
			del self.slot.files[key]

		def __iter__(self):
			return iter(self.slot.files)

		def __len__(self):
			return len(self.slot.files)

		def __contains__(self,key):
			return key in self.slot.files

		def __repr__(self):
			return f"<HASlotValuesView of {self.slot}>"

		def values(self):
			for f in self.slot.files.values():
				yield f.values

		def keys(self):
			return self.slot.files.keys()

		def items(self):
			for k,f in self.slot.files.items():
				yield k,f.values

	def __init__(self,files:dict[str,HASave]):
		self.files = files
		self.values = self.HASlotValuesView(self)

	def __getitem__(self,key):
		return self.files[key]

	@overload
	@classmethod
	def load(cls,path:str | Path, ignore_errors:Literal[True] = True)\
			-> 'tuple[HASlot,list[str]]':
		...

	@overload
	@classmethod
	def load(cls,path:str | Path, ignore_errors:Literal[False]) \
			-> 'tuple[HASlot,None]':
		...

	@classmethod
	def load(cls,path:str | Path, ignore_errors:bool = True):
		if isinstance(path,str):
			path = Path(path)
		fails = []
		files = {}
		for file in path.glob('*'):
			logging.info(f"loading {file}")
			try:
				files[str(file.relative_to(path))] = HASave.load(file)
			except Exception as e:
				logging.error(f"failed to load {file} due to a {e!r}")
				if ignore_errors:
					fails.append(str(file.relative_to(path)))
				else:
					raise ValueError("Unable to load file") from e
		return cls(files),fails if ignore_errors else None

	def dump(self,path:str | Path):
		if isinstance(path,str):
			path = Path(path)
		for file,save in self.files.items():
			save.dump(path/file)


MODE = "HASlot"


if __name__ == "__main__":
	import json
	import os
	logging.basicConfig(level=logging.INFO)
	"""
	for path in os.listdir("Slot_0"):
		print(path)
		pth = f"Slot_0/{path}"
		logging.info(f"testing {pth}")
		save = None
		with open(pth,"rb") as saveFile:
			byte = saveFile.read()
			bytearr = bytearray(byte)
			save = HASave()
			try:
				save.decode(bytearr)
			except NameError as p:
				print(p)
		try: os.mkdir("json0")
		except FileExistsError: 0
		with open(f"json0/{path}.json","w") as file:
			json.dump(save.values,file)
	"""
	parsefailures = []
	try:
		os.mkdir("json")
	except FileExistsError:
		logging.warning("json folder already exists")

	org_path = Path(r"Slot_0")

	if MODE == "HASave":
		for path in org_path.glob("*"):
			logging.info(f"parsing {path}")
			save = None
			with path.open("rb") as saveFile:
				byte = saveFile.read()
				bytearr = bytearray(byte)
				save = HASave()
				try:
					save.decode(bytearr)
				except NameError as p:
					logging.info(f"{p} failed")
					parsefailures.append(path)

			with open(f"json/{path.relative_to(org_path)}.json","w") as file:
				json.dump(save.values,file)
	elif MODE == "HASlot":
		file,parsefailures = HASlot.load(org_path)
		for k, v in file.files.items():
			with open(f"json/{k}.json","w") as file:
				json.dump(v.values,file)

	if parsefailures:
		print("the following files failed parsing")
		print("\n".join([str(i) for i in parsefailures]))
	else:
		print("all files parsed successfully")
