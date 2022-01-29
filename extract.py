from classes import HASave
import sys
import json
with open(sys.argv[1],"rb") as file:
	save = HASave(bytearray(file.read()))
	with open(f"{sys.argv[1]}.json","w") as jsonf:
		json.dump(save.values, jsonf)