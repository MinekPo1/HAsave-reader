from classes import HASave
import sys
import json
import logging
logging.basicConfig(level=logging.INFO)

if len(sys.argv) < 2:
	print("Usage: python3 extract.py <save_file>")
	sys.exit(1)

with open(sys.argv[1],"rb") as file, open(f"{sys.argv[1]}.json","w") as jsonf:
	save = HASave.from_decode(bytearray(file.read()))
	json.dump(save.values, jsonf)
