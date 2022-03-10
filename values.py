import re


def compile_all(reg: list[str]) -> list[re.Pattern[str]]:
	return [re.compile(r) for r in reg]


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
short_regex = compile_all([
	r"entry[0-9]+_count",
	r".*_n_strings",
	r".*_n_shorts",
	r".*_n_longs",
	r"entry[0-9]+_slot",
	r"perk_[^_]*$",
	r"morph[0-9]+",
	r"companion_[0-9]+_level",
	r"FREE FOLLOWER - .*_(isGenerated|isClaimed)",
	r"discovered_.*",
	r"-?[0-9]+,-?[0-9]+,id",
	r".*short[0-9]+_value",
	r"player_inner_.",
	r"player_chunk_.",
	r"zone_origin_chunk_.",
	r"companion_[0-9]+_currExp",
	r"respawn_[0-9]+_(inner.|second|minute|hour|day|month|year)",
	r".*_restart_(second|minute|hour|day|month|year)",
	r"[0-9]+,[0-9]+_numObjects",
	r"[0-9]+,[0-9]+,[0-9]+_rot",
	r"ungenerated_floor_[0-9]+_(chunk.|floorModel|floorRot|smallBudget|"
		r"largeBudget|caveartExists|caveartRot|caveartTex|hasFossil|spikes)",
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
	])
long_vars = [
	r"default",
	r"new_playerLevel",
	r"unique_id_iterator_new",
	r"unique_id_iterator"
	]
long_regex = compile_all([
	r"companion_[0-9]+(_nextExp|_pocketContainerID)",
	r".*_long[0-9]+_value",
	r"basket[0-9]+",
	r"chunk\(.*,-?[0-9]+, -?[0-9]+\)",
	r"NPCchest_[0-9]+",
	r"shack[0-9]+-zonedata",
	r"sign[0-9]+"
	])
str_vars = [
	r"player_zone",
	r"cached_language",
	r"creatureName"
	]
str_regex = compile_all([
	r".*_(string|long|short)[0-9]+_key",
	r".*_string[0-9]+_value",
	r"perk_slot_.",
	r".*_cached_status",
	r".*_cached_translation",
	r"companion_[0-9]+_creature.",
	r"companion_[0-9]+_combatName",
	r"companion_[0-9]+_companionName",
	r"companion_[0-9]+_wait_message[0-9]",
	r"companion_[0-9]+_guard_message[0-9]",
	r"FREE FOLLOWER - .*_(crit.|name)",
	r"unclaimed_freefollower_name_[0-9]+",
	r"-?[0-9]+,-?[0-9]+,mob.",
	r"ungenerated_floor_[0-9]+_(smallOre|largeOre)"
	])


def resolve_type(name:str) -> str | None:
	if name in short_vars:
		return "short"
	if name in long_vars:
		return "long"
	if name in str_vars:
		return "str"
	for regex in long_regex:
		if regex.fullmatch(name):
			return "long"
	for regex in str_regex:
		if regex.fullmatch(name):
			return "str"
	# short_regex is the longest one, so check that one last
	for regex in short_regex:
		if regex.fullmatch(name):
			return "short"
