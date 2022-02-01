from classes import HASave
import json
import logging
logging.basicConfig(level=logging.DEBUG)
with open("save_data/the_inventory","rb") as ori:
	save = HASave()
	print("decoding save")
	save.decode(bytearray(ori.read()))
	print("writing json")
	with open("the_inventory.json","w") as j:
		json.dump(save.values,j)
	print("encodeing json")
	ba = save.encode(2,save.section_count,save.values)
	print("re-writing save")
	with open("the_inventory","wb") as copy:
		copy.write(bytes(ba))
	print(save.section_count)
	print(save.values["default"])
	print("re-decoding save")
	save.decode(ba)
	print(json.dumps(save.values,indent=4))