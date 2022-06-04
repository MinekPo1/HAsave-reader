import cProfile
import logging
from classes import HASave
from pathlib import Path

orig_path = Path("Slot_0")
finl_path = Path("res")

if not finl_path.exists():
	finl_path.mkdir()

errs = []
files: dict[Path,HASave] = {}
with cProfile.Profile() as prr:
	for file in orig_path.glob("*"):
		try:
			hs = HASave()
			files[file] = hs
			hs.decode(bytearray(file.read_bytes()))
		except NameError:
			errs.append(file)

print(
	f"{len(errs)} files failed parsing, "
	f"{len(files)} files successfully parsed"
)

errs = []

with cProfile.Profile() as prw:
	for i, (file, save) in enumerate(files.items()):
		print(f"{i}/{len(files)}",end="\r")
		try:
			f2 = (finl_path / file.relative_to(orig_path))
			f2.open("wb").write(save.encode())
		except Exception as ex:
			logging.error(
				f"failed to write {file}: {ex!r} "
				)
			errs.append(file)


print(
	f"{len(errs)} files failed writing, "
	f"{len(files)-len(errs)} files successfully written"
)

prr.dump_stats("profile_read.prof")
prw.dump_stats("profile_write.prof")
print("profile_read.prof and profile_write.prof have been generated")
