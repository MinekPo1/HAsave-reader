import logging
import string
from pprint import pprint
from pathlib import Path
try:
	import prompt_toolkit
	import prompt_toolkit.completion
	import prompt_toolkit.validation
except ImportError:
	prompt_toolkit = None  # type: ignore
from sys import path

# add the root directory to the path
path.insert(0, Path(__file__).parent.parent.as_posix())

from classes import HASave  # noqa: E402


def zip2(li):
	return zip(li[::2], li[1::2])


def zipX(li,x):
	return zip(*[li[i::x] for i in range(x)])


def display_bin(bin: bytes | bytearray):
	block_size = 2
	blocks_per_line = 16
	a: list[str] = [""]
	b: list[str] = [""]
	for i in bin:
		at = f"{i:02X}"
		bt = chr(i) if chr(i) in string.printable[:-5] else "."
		if len(a[-1]) == (block_size*2+1)*blocks_per_line-1:
			a.append(at)
			b.append(bt)
		elif len(a[-1]) % (block_size*2+1) == block_size*2:
			a[-1] += f" {at}"
			b[-1] += bt
		else:
			a[-1] += at
			b[-1] += bt

	a[-1] = f"{a[-1]:<{(block_size*2+1)*blocks_per_line-1}}"
	b[-1] = f"{b[-1]:<{block_size*blocks_per_line-1}}"

	for ia,ib in zip(a,b):
		print(f"{ia} | {ib}")


def check(p: Path):
	out = HASave.load(p).encode()
	org = p.read_bytes()
	display_bin(org)
	print(f"  {len(org)} B")
	print("->")
	display_bin(out)
	print(f"  {len(out)} B")


SLOT_DIR = Path(__file__).parent.parent / "Slot_2"


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG,filename="Slot_2_diff.log")
	if prompt_toolkit is not None:
		class Validator(prompt_toolkit.validation.Validator):
			def validate(self, document):
				if document.text == "":
					return
				if prompt_toolkit is None:
					raise RuntimeError()
				if document.text not in [i.name for i in SLOT_DIR.glob("*")]:
					raise prompt_toolkit.validation.ValidationError(
						message="File not found", cursor_position=len(document.text)
					)

		class Completer(prompt_toolkit.completion.Completer):
			def get_completions(self, document, complete_event):
				if prompt_toolkit is None:
					raise RuntimeError()
				return [
					prompt_toolkit.completion.Completion(i.name, start_position=-len(document.text))
					for i in SLOT_DIR.glob("*")
					if i.name.startswith(document.text)
				]

		def get_file():
			if prompt_toolkit is None:
				raise RuntimeError()
			return SLOT_DIR / prompt_toolkit.prompt(
				"> ",
				validator=Validator(),
				completer=Completer(),
				complete_while_typing=True
			)

	else:
		def get_file():
			return SLOT_DIR / input("> ")
	while True:
		file = get_file()
		if file == SLOT_DIR:
			break
		out = HASave().load(file)
		pprint(out.values)
		check(file)
