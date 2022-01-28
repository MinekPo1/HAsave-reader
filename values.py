import re
short_vars = [
	"n_stored_items",
	"noobia_version",
	"PLAYER_ALIVE", #this is actually a boolean where a non-1 value = dead
	"n_morphed_creatures",
	"temp_nextLevelExp",
	"n_entries",
	"exists",
	"version"
	]
short_regex = [
	"entry[0-9]+_count",
	"entry[0-9]+_n_strings",
	"entry[0-9]+_n_shorts",
	"entry[0-9]+_n_longs",
	"entry[0-9]+_slot",
	"perk_[^_]*$",
	"morph[0-9]+",
	"companion_[0-9]+_level",
	"FREE FOLLOWER - .*_isGenerated",
	"FREE FOLLOWER - .*_isClaimed",
	"discovered_.*",
	"-?[0-9]+,-?[0-9]+,id",
	"entry[0-9]+_short[0-9]+_value",
	"player_inner_.",
	"player_chunk_."
	]
long_vars = [
	"default",
	"new_playerLevel",
	"unique_id_iterator_new"
	]
long_regex = [
	"companion_[0-9]+_nextExp",
	"companion_[0-9]+_pocketContainerID",
	"entry[0-9]+_long[0-9]+_value"
]
str_vars = [
	"player_zone",
	"cached_language",
	"creatureName"
	]
str_regex = [
	"entry[0-9]+_string[0-9]+_key",
	"entry[0-9]+_long[0-9]+_key",
	"entry[0-9]+_short[0-9]+_key",
	"entry[0-9]+_string[0-9]+_value",
	"perk_slot_.",
	".*_cached_status",
	".*_cached_translation",
	"companion_[0-9]+_creature.",
	"companion_[0-9]+_combatName",
	"companion_[0-9]+_companionName",
	"companion_[0-9]+_wait_message[0-9]",
	"companion_[0-9]+_guard_message[0-9]",
	"FREE FOLLOWER - .*_crit.",
	"FREE FOLLOWER - .*_name",
	"unclaimed_freefollower_name_[0-9]+",
	"-?[0-9]+,-?[0-9]+,mob."
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