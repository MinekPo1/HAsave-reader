from HAtypes import Item
import json
import traceback

with open("json/the_inventory.json","r") as inv:
	data = json.load(inv)
	items = []
	print("reading",data["n_stored_items"])
	for i in range(data["n_stored_items"]):
		try:
			items.append(Item(data,i))
		except Exception as e:
			print(data)
			print(traceback.format_exc())
	for i in items:
		print(i.__repr__())
	recover = {}
	cout = 0
	for i in items:
		d = i.toDict(cout)
		recover = recover | d
		cout += 1
	recover["n_stored_items"] = len(items)
	recover["default"] = 1
	print(recover)