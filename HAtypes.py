
def getValueOrZero(data,key):
	try:
		return data[key]
	except KeyError:
		return 0

class Item:
	def __init__(self,values,id):
		self.count = values[f"entry{id}_count"]
		self.strings = {}
		self.longs = {}
		self.shorts = {}
		n_shorts = getValueOrZero(values,f"entry{id}_n_shorts")
		n_longs = getValueOrZero(values,f"entry{id}_n_longs")
		n_strings = getValueOrZero(values,f"entry{id}_n_strings")
		for s in range(n_shorts):
			k = values[f"entry{id}_short{s}_key"]
			self.shorts[k] = values[f"entry{id}_short{s}_value"]
		for l in range(n_longs):
			k = values[f"entry{id}_long{l}_key"]
			self.longs[k] = values[f"entry{id}_longs{l}_value"]
		for st in range(n_strings):
			k = values[f"entry{id}_string{st}_key"]
			self.strings[k] = values[f"entry{id}_string{st}_value"]

	def toDict(self,id):
		data = {}
		data[f"entry{id}_count"] = self.count
		cout = 0
		for key in self.strings.keys():
			data[f"entry{id}_string{cout}_key"] = key
			data[f"entry{id}_string{cout}_value"] = self.strings[key]
			cout += 1
		data[f"entry{id}_n_strings"] = len(self.strings)
		cout = 0
		for key in self.longs.keys():
			data[f"entry{id}_long{cout}_key"] = key
			data[f"entry{id}_long{cout}_value"] = self.longs[key]
			cout += 1
		data[f"entry{id}_n_longs"] = len(self.longs)
		cout = 0
		for key in self.shorts.keys():
			data[f"entry{id}_short{cout}_key"] = key
			data[f"entry{id}_short{cout}_value"] = self.shorts[key]
			cout += 1
		data[f"entry{id}_n_shorts"] = len(self.shorts)
		return data


	def __repr__(self):
		return f"<{self.strings['item_id']} #{self.count}, str#{len(self.strings)}, long#{len(self.longs)}, short#{len(self.shorts)}>"
		
	def __str__(self):
		return f"<{self.strings['item_id']} #{self.count}>"

		