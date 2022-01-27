import re
short_vars = ["n_stored_items"]
short_regex = ["entry[0-9]+_count","entry[0-9]+_n_strings","entry[0-9]+_slot"]
long_vars = ["default"]
long_regex = []
str_vars = []
str_regex = []

def resolve_type(name)->str:
	if name in short_vars:
		return "short"
	if name in long_vars:
		return "long"
	if name in str_vars:
		return "str"
	for regex in short_regex:
		if re.search(regex,name):
			return "short"
	for regex in long_regex:
		if re.search(regex,name):
			return "long"
	for regex in str_regex:
		if re.search(regex,name):
			return "str"