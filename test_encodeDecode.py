from classes import HASave
import json
import logging
logging.basicConfig(level=logging.INFO)
with open("save_data/the_inventory","rb") as ori:
	save = HASave()
	print("decoding save")
	save.decode(bytearray(ori.read()))
	print("writing json")
	with open("the_inventory.json","w") as j:
		json.dump(save.values,j)
	print("encodeing json")
	logging.basicConfig(level=logging.DEBUG,force=True)
	ba = save.encode(2,save.section_count,save.values)
	print("re-writing save")
	with open("the_inventory","wb") as copy:
		copy.write(ba)
	print(save.section_count)
	print(save.values["default"])