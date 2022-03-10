import cProfile
from classes import HASlot

with cProfile.Profile() as pr:
	slot,errs = HASlot.load("Slot_2")

print(f"{len(errs)} files failed")

pr.dump_stats("profile.prof")
