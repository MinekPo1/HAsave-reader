from lib2to3.pgen2.parse import ParseError
import logging
import re
from tkinter import N
from values import *

specialKeyRegex = [
	"basket[0-9]+",
	"chunk\(.*,-?[0-9]+, -?[0-9]+\)",
	"NPCchest_[0-9]+",
	"shack[0-9]+-zonedata"
]

class HASave:
	__offset__:int = 0
	def __init__(self):
		self.data = bytearray([])
		self.save_version = 0
		self.section_count = 0
		self.values = {}
		self.__offset__ = 0
	
	def parse(self, ba:bytearray):
		self.data = ba
		self.save_version = self.__pop_byte__()
		self.section_count = self.__ext_short__()
		while 1==1:
			try:
				key, l = self.__ext_str__(False)
			except IndexError as err:
				break
			if (l == 0): continue
			if (l == 1): self.__pop_byte__();continue
			if len(key) == 0: continue
			logging.debug(f"read key: {key}, len: {l}")
			var_type = resolve_type(key)
			var = None
			logging.debug(f"type: {var_type}")
			if var_type == "short":var = self.__ext_short__()
			if var_type == "long":var  = self.__ext_long__()
			if var_type == "str":var = self.__ext_str__(True)[0]
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

	def __ext_short__(self)->int:
		low = f"{self.__pop_byte__():b}"
		high = f"{self.__pop_byte__():b}"
		while len(high) < 8:
			high = "0"+high
		while len(low) < 8:
			low = "0"+low
		val = int(high+low,2)
		if val >= 32768: val -= 65536
		return val
	def __ext_long__(self)->int:
		lowest = f"{self.__pop_byte__():b}"
		low = f"{self.__pop_byte__():b}"
		high = f"{self.__pop_byte__():b}"
		highest = f"{self.__pop_byte__():b}"
		val = int(highest+high+low+lowest,2)
		if val >= 2147483648: val -= 4294967296
		return val
	def __ext_str__(self,is_value:bool) -> tuple[str, int]:
		str_len = self.__pop_byte__()
		if str_len == 0: return "",0
		if str_len%2 == 1: return "",1
		if (str_len<10) and (not is_value): return "",1
		if (str_len>100): return "",1
		string = ""
		nulCounter = 0
		for _ in range(str_len):
			if nulCounter > 2: return "",1
			val = self.__pop_byte__()
			if val == 0: nulCounter +=1; continue
			string += chr(val)
			nulCounter = 0
		self.__pop_byte__()
		return string,str_len
	def __repr__(self):
		return f"<HAsave v:{self.save_version} obj#: {len(self.values)}>"
	def __getitem__(self,key):
		return self.values[key]

if __name__ == "__main__":
	import json, os
#	logging.basicConfig(level=logging.DEBUG)
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
				save.parse(bytearr)
			except NameError as p:
				print(p)
		try: os.mkdir("json")
		except FileExistsError: 0
		with open(f"json/{path}.json","w") as file:
			json.dump(save.values,file)
