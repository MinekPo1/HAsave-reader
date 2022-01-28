import re
short_vars = [
	"n_stored_items",
	"player_chunk_x",
	"player_inner_x",
	"player_chunk_x",
	"player_inner_y",
	"player_inner_z"
	]
short_regex = [
	"entry[0-9]+_count",
	"entry[0-9]+_n_strings",
	"entry[0-9]+_slot",
	"perk_[^_]*$"
	]
long_vars = [
	"default",
	"entry1_n_strings"
	]
long_regex = []
str_vars = [
	"player_zone"
	]
str_regex = [
	"entry[0-9]+_string[0-9]+_key",
	"entry[0-9]+_string[0-9]+_value",
	"perk_slot_."
	]

def resolve_type(name:str)->str|None:
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