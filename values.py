import re
short_vars = [
	r"n_stored_items",
	r"noobia_version",
	r"PLAYER_ALIVE",  # this is actually a boolean where a non-1 value = dead
	r"n_morphed_creatures",
	r"temp_nextLevelExp",
	r"n_entries",
	r"exists",
	r"version",
	r"n_respawns",
	r"biome",
	r"floor-tex-index",
	r"floor-rot",
	r"n_ungenerated_floors",
	r"speed",
	r"slices",
	r"save_song_id_iterator",
	r"n_unclaimed_freefollower_names",
	r"currentEXP",
	r"numRebreeds",
	r"skillPointsSpendable",
	r"zone_item_n_strings",
	r"zone_item_n_longs",
	r"zone_item_n_shorts",
	r"outer_item_zone",
	r"outer_item_rot",
	r"n_teleporters",
	r"cave_exists",
	r"floor-model-id"
	]
short_regex = [
	r"entry[0-9]+_count",
	r".*_n_strings",
	r".*_n_shorts",
	r".*_n_longs",
	r"entry[0-9]+_slot",
	r"perk_[^_]*$",
	r"morph[0-9]+",
	r"companion_[0-9]+_level",
	r"FREE FOLLOWER - .*_isGenerated",
	r"FREE FOLLOWER - .*_isClaimed",
	r"discovered_.*",
	r"-?[0-9]+,-?[0-9]+,id",
	r".*short[0-9]+_value",
	r"player_inner_.",
	r"player_chunk_.",
	r"zone_origin_chunk_.",
	r"companion_[0-9]+_currExp",
	r"respawn_[0-9]+_inner.",
	r"respawn_[0-9]+_second",
	r"respawn_[0-9]+_minute",
	r"respawn_[0-9]+_hour",
	r"respawn_[0-9]+_day",
	r"respawn_[0-9]+_month",
	r"respawn_[0-9]+_year",
	r".*_restart_second",
	r".*_restart_minute",
	r".*_restart_hour",
	r".*_restart_day",
	r".*_restart_month",
	r".*_restart_year",
	r"[0-9]+,[0-9]+_numObjects",
	r"[0-9]+,[0-9]+,[0-9]+_rot",
	r"ungenerated_floor_[0-9]+_chunk.",
	r"ungenerated_floor_[0-9]+_floorModel",
	r"ungenerated_floor_[0-9]+_floorRot",
	r"ungenerated_floor_[0-9]+_smallBudget",
	r"ungenerated_floor_[0-9]+_largeBudget",
	r"ungenerated_floor_[0-9]+_caveartExists",
	r"ungenerated_floor_[0-9]+_caveartRot",
	r"ungenerated_floor_[0-9]+_caveartTex",
	r"ungenerated_floor_[0-9]+_hasFossil",
	r"ungenerated_floor_[0-9]+_spikes",
	r"slice-[0-9]+-n_instruments",
	r"slice-[0-9]+-instrument-[0-9]+-type",
	r"slice-[0-9]+-instrument-[0-9]+-n_pressed",
	r"slice-[0-9]+-instrument-[0-9]+-pressed-[0-9]+",
	r"slice-[0-9]+-instrument-[0-9]+-length-[0-9]+",
	r"savesong[0-9]+-.",
	r".*_progress",
	r".*_restart_dateSet",
	r".*_completions",
	r".*_isCollected",
	r"stat[0-9]+",
	r"musicboxplaying_[0-9]+",
	r"interior_model_chunk.",
	r"interior_model_inner.",
	r"biome-mob-."
	]
long_vars = [
	r"default",
	r"new_playerLevel",
	r"unique_id_iterator_new",
	r"unique_id_iterator"
	]
long_regex = [
	r"companion_[0-9]+_nextExp",
	r"companion_[0-9]+_pocketContainerID",
	r".*_long[0-9]+_value",
	r"basket[0-9]+",
	r"chunk\(.*,-?[0-9]+, -?[0-9]+\)",
	r"NPCchest_[0-9]+",
	r"shack[0-9]+-zonedata",
	r"sign[0-9]+"
	]
str_vars = [
	r"player_zone",
	r"cached_language",
	r"creatureName"
	]
str_regex = [
	r".*_string[0-9]+_key",
	r".*_long[0-9]+_key",
	r".*_short[0-9]+_key",
	r".*_string[0-9]+_value",
	r"perk_slot_.",
	r".*_cached_status",
	r".*_cached_translation",
	r"companion_[0-9]+_creature.",
	r"companion_[0-9]+_combatName",
	r"companion_[0-9]+_companionName",
	r"companion_[0-9]+_wait_message[0-9]",
	r"companion_[0-9]+_guard_message[0-9]",
	r"FREE FOLLOWER - .*_crit.",
	r"FREE FOLLOWER - .*_name",
	r"unclaimed_freefollower_name_[0-9]+",
	r"-?[0-9]+,-?[0-9]+,mob.",
	r"ungenerated_floor_[0-9]+_smallOre",
	r"ungenerated_floor_[0-9]+_largeOre"
	]


def resolve_type(name:str) -> str | None:
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
