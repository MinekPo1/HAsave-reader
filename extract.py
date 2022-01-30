from classes import HASave
import sys
import json
import logging
logging.basicConfig(level=logging.DEBUG)

with open(sys.argv[1],"rb") as file:
	save = HASave()
	save.decode(bytearray(file.read()))
	with open(f"{sys.argv[1]}.json","w") as jsonf:
		json.dump(save.values, jsonf)