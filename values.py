import re
short_vars = [
	"n_stored_items",
	"noobia_version",
	"PLAYER_ALIVE", #this is actually a boolean where a non-1 value = dead
	"n_morphed_creatures",
	"temp_nextLevelExp",
	"n_entries",
	"exists",
	"version",
	"n_respawns",
	"biome",
	"floor-tex-index",
	"floor-rot",
	"n_ungenerated_floors",
	"speed",
	"slices",
	"save_song_id_iterator",
	"n_unclaimed_freefollower_names",
	"currentEXP",
	"numRebreeds",
	"skillPointsSpendable",
	"zone_item_n_strings",
	"zone_item_n_longs",
	"zone_item_n_shorts",
	"outer_item_zone",
	"outer_item_rot",
	"n_teleporters",
	"cave_exists",
	"floor-model-id"
	]
short_regex = [
	"entry[0-9]+_count",
	".*_n_strings",
	".*_n_shorts",
	".*_n_longs",
	"entry[0-9]+_slot",
	"perk_[^_]*$",
	"morph[0-9]+",
	"companion_[0-9]+_level",
	"FREE FOLLOWER - .*_isGenerated",
	"FREE FOLLOWER - .*_isClaimed",
	"discovered_.*",
	"-?[0-9]+,-?[0-9]+,id",
	".*short[0-9]+_value",
	"player_inner_.",
	"player_chunk_.",
	"zone_origin_chunk_.",
	"companion_[0-9]+_currExp",
	"respawn_[0-9]+_inner.",
	"respawn_[0-9]+_second",
	"respawn_[0-9]+_minute",
	"respawn_[0-9]+_hour",
	"respawn_[0-9]+_day",
	"respawn_[0-9]+_month",
	"respawn_[0-9]+_year",
	".*_restart_second",
	".*_restart_minute",
	".*_restart_hour",
	".*_restart_day",
	".*_restart_month",
	".*_restart_year",
	"[0-9]+,[0-9]+_numObjects",
	"[0-9]+,[0-9]+,[0-9]+_rot",
	"ungenerated_floor_[0-9]+_chunk.",
	"ungenerated_floor_[0-9]+_floorModel",
	"ungenerated_floor_[0-9]+_floorRot",
	"ungenerated_floor_[0-9]+_smallBudget",
	"ungenerated_floor_[0-9]+_largeBudget",
	"ungenerated_floor_[0-9]+_caveartExists",
	"ungenerated_floor_[0-9]+_caveartRot",
	"ungenerated_floor_[0-9]+_caveartTex",
	"ungenerated_floor_[0-9]+_hasFossil",
	"ungenerated_floor_[0-9]+_spikes",
	"slice-[0-9]+-n_instruments",
	"slice-[0-9]+-instrument-[0-9]+-type",
	"slice-[0-9]+-instrument-[0-9]+-n_pressed",
	"slice-[0-9]+-instrument-[0-9]+-pressed-[0-9]+",
	"slice-[0-9]+-instrument-[0-9]+-length-[0-9]+",
	"savesong[0-9]+-.",
	".*_progress",
	".*_restart_dateSet",
	".*_completions",
	".*_isCollected",
	"stat[0-9]+",
	"musicboxplaying_[0-9]+",
	"interior_model_chunk.",
	"interior_model_inner.",
	"biome-mob-."
	]
long_vars = [
	"default",
	"new_playerLevel",
	"unique_id_iterator_new",
	"unique_id_iterator"
	]
long_regex = [
	"companion_[0-9]+_nextExp",
	"companion_[0-9]+_pocketContainerID",
	".*_long[0-9]+_value",
	"basket[0-9]+",
	"chunk\(.*,-?[0-9]+, -?[0-9]+\)",
	"NPCchest_[0-9]+",
	"shack[0-9]+-zonedata",
	"sign[0-9]+"
	]
str_vars = [
	"player_zone",
	"cached_language",
	"creatureName"
	]
str_regex = [
	".*_string[0-9]+_key",
	".*_long[0-9]+_key",
	".*_short[0-9]+_key",
	".*_string[0-9]+_value",
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
	"-?[0-9]+,-?[0-9]+,mob.",
	"ungenerated_floor_[0-9]+_smallOre",
	"ungenerated_floor_[0-9]+_largeOre"
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