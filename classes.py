import logging
import re
from values import *

specialKeyRegex = [
	"basket[0-9]+",
	"chunk\(.*,-?[0-9]+, -?[0-9]+\)",
	"NPCchest_[0-9]+",
	"shack[0-9]+-zonedata",
	"sign[0-9]+"
]

class HASave:
	__offset__:int = 0
	def __init__(self):
		self.data = bytearray([])
		self.save_version = 0
		self.section_count = 0
		self.values = {}
		self.__offset__ = 0
	
	def encode(self,version:int,sections:int,data:dict)->bytearray:
		ba = bytearray()
		print("serilising")
		print(data)
		logging.debug("writing version to bytearray")
		ba.insert(0,version%255)
		logging.debug("inserting section count")
		self.__insert_short__(ba,sections)
		for key in data.keys():
			self.__insert_str__(ba,key)
			logging.debug(f"inserting key: {key}")
			datatype = resolve_type(key)
			if datatype == "short":self.__insert_short__(ba,data[key])
			if datatype == "long":self.__insert_long__(ba,data[key])
			if datatype == "str":self.__insert_str__(ba,data[key])
			if datatype == None: raise ValueError(f"Key: {key} has no type associated")
		return ba

	def decode(self, ba:bytearray):
		self.data = ba
		self.save_version = self.__pop_byte__()
		self.section_count = self.__extract_short__()
		while 1==1:
			try:
				key, l = self.__extract_str__()
			except IndexError as err:
				break
			if (l == 0): continue
			if (l == 1): continue
			if len(key) == 0: continue
			logging.debug(f"read key: {key}, len: {l}")
			var_type = resolve_type(key)
			var = None
			logging.debug(f"type: {var_type}")
			if var_type == "short":var = self.__extract_short__()
			if var_type == "long":var  = self.__extract_long__()
			if var_type == "str":var = self.__extract_str__()[0]
			if var == None:
				raise NameError(f"Parse Error @ Offset: {self.__offset__} {key}")
			logging.debug(f"value: {var}")
			if self.section_count >= 2:
				for regex in specialKeyRegex:
					if re.search(regex,key):
						superKey = key
				if not (superKey in self.values.keys()):
					self.values[superKey] = {}
				self.values[superKey][key] = var
			else:
				self.values[key] = var

	def __pop_byte__(self)->int:
		self.__offset__ += 1
		return self.data.pop(0)
	def __get_hex__value__(self)->str:
		val = f"{self.__pop_byte__():02x}"
		if len(val) <2:
			val = "0"+val
		return val

	def __extract_short__(self,signed=True,requireLowNonZero=False)->int:
		lh = self.__get_hex__value__()
		if (lh == '00') and requireLowNonZero: 
			return 0
		hh = self.__get_hex__value__()
		hs = lh+hh
		val = int.from_bytes(
			bytearray.fromhex(
				hs,
			),
			'little',
			signed=signed
		)
		return val
	def __extract_long__(self,signed=True)->int:
		llh = self.__get_hex__value__()
		lh = self.__get_hex__value__()
		hh = self.__get_hex__value__()
		hhh = self.__get_hex__value__()
		hs = llh + lh + hh + hhh
		val = int.from_bytes(
			bytearray.fromhex(
				hs
			),
			'little',
			signed=signed
		)
		return val
	def __extract_str__(self) -> tuple[str, int]:
		str_len = self.__extract_short__(signed=False,requireLowNonZero=True)
		if str_len == 0:
			logging.debug("zero-length string")
			return "",0
		if str_len%2 == 1:
			logging.debug("uneven length string")
			return "",1
		string = ""
		for _ in range(int(str_len/2)):
			chrv = self.__extract_short__(signed=False)
			try:
				val = chr(chrv)
			except ValueError as ve:
				print(ve)
				print(f"hexvalue: {chrv:x}")
			if val == '\x00': return "",1
			string += val
		return string,str_len
	
	def __insert_short__(self,ba:bytearray,value:int):
		logging.debug(f"writing short: {value}")
		val = value
		if val < 0:
			val += 65536
		if val < 0: raise ValueError("Value must be more then -32769 but less then 32768")
		bits = f"{val:b}"
		while len(bits) < 16:
			bits = "0" + bits
		byte = [bits[i:i+8] for i in range(0, len(bits), 8)]
		high = int(byte.pop(0),2)
		low = int(byte.pop(0),2)
		logging.debug(f"(shrt) inserting {low:02x} {high:02x}")
		ba.append(low)
		ba.append(high)
	def __insert_long__(self,ba:bytearray,value:int):
		logging.debug(f"writing long: {value}")
		val = value
		if val < 0:
			val += 4294967296
		if val < 0: raise ValueError("Value must be more then -2147483649 but less then 2147483648")
		bits = f"{val:b}"
		while len(bits) < 32:
			bits = "0" + bits
		byte = [bits[i:i+8] for i in range(0, len(bits), 8)]
		highest = int(byte.pop(0),2)
		high = int(byte.pop(0),2)
		low = int(byte.pop(0),2)
		lowest = int(byte.pop(0),2)
		ba.append(lowest)
		ba.append(low)
		ba.append(high)
		ba.append(highest)
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

if __name__ == "__main__":
	import json, os
#	logging.basicConfig(level=logging.DEBUG)
#	for path in os.listdir("Slot_0"):
#		print(path)
#		pth = f"Slot_0/{path}"
#		logging.info(f"testing {pth}")
#		save = None
#		with open(pth,"rb") as saveFile:
#			byte = saveFile.read()
#			bytearr = bytearray(byte)
#			save = HASave()
#			try:
#				save.decode(bytearr)
#			except NameError as p:
#				print(p)
#		try: os.mkdir("json0")
#		except FileExistsError: 0
#		with open(f"json0/{path}.json","w") as file:
#			json.dump(save.values,file)
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
		try: os.mkdir("json")
		except FileExistsError: 0
		with open(f"json/{path}.json","w") as file:
			json.dump(save.values,file)
	print("the following files failed parsing")
	print(parsefailures)
