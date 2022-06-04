from classes import HASave
import json
import logging
try:
	import deepdiff
except ImportError:
	deepdiff = None
logging.basicConfig(level=logging.INFO)
with open("save_data/the_inventory","rb") as ori:
	save = HASave()
	print("decoding save")
	save.decode(bytearray(ori.read()))
	o = save.values.copy()
	print("writing json")
	with open("the_inventory.json","w") as j:
		json.dump(save.values,j)
	print("encodeing json")
	ba = save.encode(2,save.section_count,save.values)
	print("re-writing save")
	with open("the_inventory","wb") as copy:
		copy.write(bytes(ba))
	print(save.section_count)
	# print(save.values["default"])
	print("re-decoding save")
	save.decode(ba)
	if deepdiff:
		print(json.dumps(deepdiff.DeepDiff(o,save.values),default=str,indent=4))
	else:
		print(json.dumps(save.values,indent=4))
		print(save.values == o)
