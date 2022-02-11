class Item:
	strings: dict[str,str]
	longs: dict[str,int]
	shorts: dict[str,int]

	def __init__(self,values:dict[str,"int | str"],id:int):
		self.count = values[f"entry{id}_count"]
		self.strings = {}
		self.longs = {}
		self.shorts = {}
		n_shorts:  int = values.get(f"entry{id}_n_shorts", 0)  # type:ignore
		n_longs:   int = values.get(f"entry{id}_n_longs",  0)  # type:ignore
		n_strings: int = values.get(f"entry{id}_n_strings",0)  # type:ignore
		for sh in range(n_shorts):
			k = values[f"entry{id}_short{sh}_key"]
			self.shorts[k]   = values[f"entry{id}_short{sh}_value"]  # type:ignore
		for ln in range(n_longs):
			k = values[f"entry{id}_long{ln}_key"]
			self.longs[k]    = values[f"entry{id}_longs{ln}_value"]  # type:ignore
		for st in range(n_strings):
			k = values[f"entry{id}_string{st}_key"]
			self.strings[k] = values[f"entry{id}_string{st}_value"]  # type:ignore

	def toDict(self,id):
		data = {f"entry{id}_count": self.count}
		for count, key in enumerate(self.strings.keys()):
			data[f"entry{id}_string{count}_key"] = key
			data[f"entry{id}_string{count}_value"] = self.strings[key]
		data[f"entry{id}_n_strings"] = len(self.strings)
		for count, key in enumerate(self.longs.keys()):
			data[f"entry{id}_long{count}_key"] = key
			data[f"entry{id}_long{count}_value"] = self.longs[key]
		data[f"entry{id}_n_longs"] = len(self.longs)
		for count, key in enumerate(self.shorts.keys()):
			data[f"entry{id}_short{count}_key"] = key
			data[f"entry{id}_short{count}_value"] = self.shorts[key]
		data[f"entry{id}_n_shorts"] = len(self.shorts)
		return data

	def __repr__(self):
		return (
			f"<{self.strings['item_id']} #{self.count}, str#{len(self.strings)}, "
			f"long#{len(self.longs)}, short#{len(self.shorts)}>"
		)
		# is all this information nessery?
		# `item_id` seems to be the only thing unique between objects

	def __str__(self):
		return f"<{self.strings['item_id']} #{self.count}>"
