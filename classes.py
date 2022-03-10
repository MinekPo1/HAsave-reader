import logging
import re
from values import *

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

	def encode(self,version:int,sections:int,data:dict) -> bytearray:
		ba = bytearray()
		logging.info("serilising")
		logging.info(data)
		logging.debug("writing version to bytearray")
		ba.insert(0, version % 255)
		logging.debug("inserting section count")
		self.__insert_short__(ba,sections)
		for key, value in data.items():
			self.__insert_str__(ba,key)
			logging.debug(f"inserting key: {key}")
			datatype = resolve_type(key)
			if datatype == "short":
				self.__insert_short__(ba,value)
			if datatype == "long":
				self.__insert_long__(ba,value)
			if datatype == "str":
				self.__insert_str__(ba, value)
			if datatype is None:
				raise ValueError(f"Key: {key} has no type associated")
		return ba

	def decode(self, ba:bytearray):
		self.data = ba
		self.save_version = self.__pop_byte__()
		self.section_count = self.__extract_short__()
		while True:
			try:
				key, lenght = self.__extract_str__()
			except IndexError:
				break
			if (lenght == 0 or lenght == 1 or len(key) == 0):
				continue
			logging.debug(f"read key: {key}, len: {lenght}")
			var_type = resolve_type(key)
			var = None
			logging.debug(f"type: {var_type}")
			if var_type == "short":
				var = self.__extract_short__()
			if var_type == "long":
				var  = self.__extract_long__()
			if var_type == "str":
				var = self.__extract_str__()[0]
			if var is None:
				raise NameError(f"Parse Error @ Offset: {self.__offset__} {key}")
			logging.debug(f"value: {var}")
			if self.section_count >= 2:
				superKey = None
				for regex in specialKeyRegex:
					if re.search(regex,key):
						superKey = key
				# if superKey is None:
				# 	raise ValueError(f"Key: {key} is not a special key")
				if superKey not in self.values.keys():
					self.values[superKey] = {}
				self.values[superKey][key] = var
			else:
				self.values[key] = var

	def __pop_byte__(self)->int:
		self.__offset__ += 1
		return self.data.pop(0)

	def __get_hex__value__(self) -> str:
		val = f"{self.__pop_byte__():02x}"
		if len(val) <2:
			val = f'0{val}'
		return val

	def __extract_short__(self,signed:bool = True,requireLowNonZero:bool = False)\
			-> int:
		lh = self.__get_hex__value__()
		if (lh == '00') and requireLowNonZero:
			return 0
		hh = self.__get_hex__value__()
		hs = lh+hh
		return int.from_bytes(
			bytearray.fromhex(
				hs,
			),
			'little',
			signed=signed
		)

	def __extract_long__(self,signed=True) -> int:
		"""
		llh = self.__get_hex__value__()
		lh = self.__get_hex__value__()
		hh = self.__get_hex__value__()
		hhh = self.__get_hex__value__()
		hs = llh + lh + hh + hhh
		"""
		hs = "".join([self.__get_hex__value__() for _ in range(4)])
		return int.from_bytes(
			bytearray.fromhex(
				hs
			),
			'little',
			signed=signed
		)

	def __extract_str__(self) -> tuple[str, int]:
		str_len = self.__extract_short__(signed=False,requireLowNonZero=True)
		if str_len == 0:
			logging.debug("zero-length string")
			return "",0
		if str_len % 2 == 1:
			logging.debug("uneven length string")
			return "",1
		string = ""
		for _ in range(int(str_len/2)):
			chrv = self.__extract_short__(signed=False)
			try:
				val = chr(chrv)
			except ValueError as ve:
				logging.debug(f"{chrv} is not a valid char")
				raise ve from ve
			if val == '\x00':
				return "",1
			string += val
		return string,str_len

	def __insert_short__(self,ba:bytearray,value:int):
		logging.debug(f"writing short: {value}")
		if value < 0:
			value += 65536
		if value < 0 or value > 65535:
			raise ValueError("Value must be more then -32769 but less then 32768")

		bits = f"{value:0>16b}"
		byte = [bits[i:i+8] for i in range(0, len(bits), 8)]
		for _ in range(2):
			ba.append(int(byte.pop(0),2))

	def __insert_long__(self,ba:bytearray,value:int):
		logging.debug(f"writing long: {value}")
		val = value
		if val < 0:
			val += 4294967296
		if val < 0 or val > 4294967295:
			raise ValueError(
				"Value must be more then -2147483649 "
				"but less then 2147483648"
			)
		bits = f"{val:0>32b}"
		byte = [bits[i:i+8] for i in range(0, len(bits), 8)]
		for _ in range(4):
			ba.append(int(byte.pop(0),2))

	def __insert_str__(self,ba:bytearray,string:str):
		logging.debug(f"writing string: {string}")
		if len(string) > 125:
			raise ValueError('string must be less then 125 charachters long')
		b = bytearray()
		for char in string:
			b.append(int.from_bytes(char.encode(),'little'))
			b.append(0)
		b.insert(0,0)
		b.insert(0,len(b)-1)
		for byte in b:
			ba.append(byte)

	def __repr__(self):
		return f"<HAsave v:{self.save_version} obj#: {len(self.values)}>"

	def __getitem__(self,key):
		return self.values[key]

	@classmethod
	def from_decode(cls, ba:bytearray):
		ret = cls()
		ret.decode(ba)
		return ret


if __name__ == "__main__":
	import json
	import os
	logging.basicConfig(level=logging.DEBUG)
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
	for path in os.listdir("save_data"):
		print(path)
		pth = f"save_data/{path}"
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
				parsefailures.append(path)
		try:
			os.mkdir("json")
		except FileExistsError:
			pass
		with open(f"json/{path}.json","w") as file:
			json.dump(save.values,file)
	print("the following files failed parsing")
	print("\n".join(parsefailures))
