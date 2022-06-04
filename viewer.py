from __future__ import annotations
import logging
import string
from pprint import pprint
from pathlib import Path
from typing import Callable, ClassVar, Literal, TypeVar, Sequence
try:
	import prompt_toolkit
	import prompt_toolkit.completion
	import prompt_toolkit.validation
except ImportError:
	prompt_toolkit = None  # type: ignore
from classes import HASave

T = TypeVar("T")


def zip2(li: Sequence[T]) -> zip[tuple[T,T]]:
	return zip(li[::2], li[1::2])


def zipX(li: Sequence[T],x: int) -> zip[tuple[T,...]]:
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
	if display_mode["raw"] & 1:
		display_bin(org)
		print(f"  {len(org)} B")
	if display_mode["raw"] == 3:
		print("->")
	if display_mode["raw"] & 2:
		display_bin(out)
		print(f"  {len(out)} B")


def save_context():
	delete = False
	with (Path(__file__).parent / ".viewer_context").open('w') as f:
		if display_mode != {"raw":3,"dict":3}:
			f.write(
				"display_mode = "
				+ str(display_mode['dict'] << 2 + display_mode['raw'])
				+ "\n"
			)
		if SLOT_DIR.name != "Slot_0":
			f.write(f"SLOT_DIR = {SLOT_DIR}\n")
		if f.seek(0,1):
			# nothing to save
			# mark the file for deletion
			delete = True
	if delete:
		(Path(__file__).parent / ".viewer_context").unlink()


def load_context():
	global SLOT_DIR
	with (Path(__file__).parent / ".viewer_context").open('r') as f:
		for line in f:
			if line.startswith("display_mode = "):
				display_mode["dict"] = (int(line[15:]) >> 2) & 3
				display_mode["raw"] = int(line[15:]) & 3
			elif line.startswith("SLOT_DIR = "):
				SLOT_DIR = Path(line[11:-1])
			else:
				raise ValueError(f"unknown line: {line}")


def changes_context(func: Callable[..., None]) -> Callable[..., None]:
	def wrapper(*args, **kwargs):
		func(*args, **kwargs)
		save_context()
	wrapper.__annotations__ = func.__annotations__
	return wrapper


SLOT_DIR = Path(__file__).parent / "Slot_2"


Tm = TypeVar("Tm", bound=Callable)

display_mode_text = [
	"off",
	"before",
	"after",
	"both",
]

display_mode: dict[str,int] = {
	"dict": 3,
	"raw": 3
}


class Command:
	commands: ClassVar[dict[str,Command]] = {}
	initialised: bool = False

	@classmethod
	def __new__(cls, *args) -> Command:
		logging.info("__new__: "+' '.join(map(repr,args)))
		if args[1] not in cls.commands:
			logging.info("__new__: returning new command")
			return super().__new__(cls)
		logging.info(f"__new__: {args[1]!r} in cache")
		if args[2:]:
			logging.info("__new__: subcommand "+' '.join(map(repr,args[2:])))
			return cls.commands[args[1]].subcommand(*args[2:])
		logging.info("__new__: returning from cache")
		return cls.commands[args[1]]

	def __init__(self, name: str, *args: str):
		logging.info(f"__init__: {repr(name)}")
		if self.initialised:
			logging.info("__init__: already initialised")
			return
		self.name = name
		self.commands[name] = self
		self.methods: dict[tuple[Literal["number","string"],...],Callable] = {}
		self.subcommands: dict[str,Command] = {}
		if args:
			self.subcommand(*args)
		self.initialised = True
		logging.info(f"__init__: {repr(name)} done")

	def __call__(self,method: Callable) -> Command:
		# analize the method for argument types
		types = [
			"number" if t == "int" else
			"string" if t == "str" else
			"INVALID"
			for i,t in method.__annotations__.items()
			if i != "return"
		]
		if "INVALID" in types:
			raise TypeError(
				f"method has invalid or unknown types "
				f"(`{list(method.__annotations__.keys())[types.index('INVALID')]}` has "
				f"type {list(method.__annotations__.values())[types.index('INVALID')]})"
			)
		self.methods[tuple(types)] = method  # type:ignore

		return self

	def subcommand(self, name: str, *args: str) -> Command:
		if name in self.subcommands:
			logging.info(f"subcommand: {name!r} in cache")
			if args:
				return self.subcommands[name].subcommand(*args)
			return self.subcommands[name]
		logging.info(f"subcommand: new subcommand! {name!r}")
		self.subcommands[name] = Command(f"{self.name} {name}")
		if args:
			return self.subcommands[name].subcommand(*args)
		return self.subcommands[name]

	def execute(self, *args: str) -> None:
		# just in case, convert all args to strings
		args = tuple(map(str,args))
		# check for subcommands
		if args:
			subcommand = self.subcommands.get(args[0])
			if subcommand is not None:
				subcommand.execute(*args[1:])
				return
		# find methods with matching argument count
		methods = list(filter(
			lambda m: len(m[0]) == len(args),
			self.methods.items()
		))
		# check which (if any) of the methods match the arguments
		methods = list(filter(
			lambda m: all(
				i != "number" or j.isnumeric()
				for i,j in zip(m[0],args)
			),
			methods
		))

		# execute the first method found
		if not methods:
			raise TypeError(f"no method found for {args}")
		# convert arguments to the correct type
		nargs = tuple(
			int(j) if i == "number" else j
			for i,j in zip(methods[0][0],args)
		)
		methods[0][1](*nargs)

	def validate_arg(self, *arg: str) -> bool:
		# check for subcommands
		if arg:
			subcommand = self.subcommands.get(arg[0])
			if subcommand is not None:
				return subcommand.validate_arg(*arg[1:])
		# find methods with matching argument count
		methods = filter(
			lambda m: len(m[0]) == len(arg),
			self.methods.items()
		)
		# check which (if any) of the methods match the arguments
		methods = filter(
			lambda m: all(
				i[1:] == j if i.startswith(":") else
				i != "number" or j.isnumeric()
				for i,j in zip(m[0],arg)
			),
			methods
		)

		return bool(list(methods))

	@classmethod
	def validate(cls, command: str) -> tuple[bool,str]:
		if not command.startswith("@"):
			return False, "command must start with @"
		command_split = command[1:].split()
		if not command_split:
			return False, "empty command"
		if command_split[0] not in cls.commands:
			return False, f"unknown command {command_split[0]}"
		# validate the arguments
		return cls.commands[command_split[0]].validate_arg(*command_split[1:]), \
			"invalid arguments"


@Command("hex")
def _(value: int) -> None:
	print(hex(value))


@Command("mode")
def _() -> None:
	for k,v in display_mode.items():
		print(f"{k: >10} mode: {display_mode_text[v]}")


@Command("mode")
@changes_context
def _(mode: int) -> None:
	if mode not in range(16):
		print(f"value must be in range 0-16, got {mode}")
		return
	d_mode = mode // 4
	r_mode = mode & 3
	print(f"dict mode is now {display_mode_text[d_mode]}")
	print(f" raw mode is now {display_mode_text[r_mode]}")
	display_mode["dict"] = d_mode
	display_mode["raw"]  = r_mode


@Command("mode")
@changes_context
def _(d_mode: str,r_mode: str) -> None:
	Command("mode","dict").execute(d_mode)
	Command("mode","raw").execute(r_mode)


@Command("mode","dict")
def _() -> None:
	print(f"      dict mode: {display_mode_text[display_mode['dict']]}")


@Command("mode","dict")
@changes_context
def _(mode: int) -> None:
	if mode not in range(4):
		print(f"value must be in range 0-3, got {mode}")
		return
	print(f"dict mode is now {display_mode_text[mode]}")
	display_mode["dict"] = mode


@Command("mode","dict")
@changes_context
def _(mode: str) -> None:
	if mode not in display_mode_text:
		print(f"unknown mode {mode}")
		print("valid modes:",*display_mode_text)
		return
	print(f"dict mode is now {mode}")
	display_mode["dict"] = display_mode_text.index(mode)


@Command("mode","raw")
def _() -> None:
	print(f"       raw mode: {display_mode_text[display_mode['raw']]}")


@Command("mode","raw")
@changes_context
def _(mode: int) -> None:
	if mode not in range(4):
		print(f"value must be in range 0-3, got {mode}")
		return
	print(f" raw mode is now {display_mode_text[mode]}")
	display_mode["raw"] = mode


@Command("mode","raw")
@changes_context
def _(mode: str) -> None:
	if mode not in display_mode_text:
		print(f"unknown mode {mode}")
		print("valid modes: off, before, after, both")
		return
	print(f" raw mode is now {mode}")
	display_mode["raw"] = display_mode_text.index(mode)


@Command("view")
def _(r_path: str) -> None:
	path = SLOT_DIR / r_path
	if not path.exists():
		print(f"{r_path} does not exist")
		return
	if path.is_dir():
		print(f"{r_path} is a directory")
		return
	with path.open("rb") as f:
		if display_mode["dict"] & 1:
			try:
				out = HASave.load(path)
				pprint(out.values)
			except Exception as e:
				print(f"unable to show dict due to {e.__class__.__name__}: ", end="")
				try:
					print(e)
				except UnicodeEncodeError:
					print(repr(e))
		if display_mode["raw"] & 1:
			display_bin(f.read())


@Command("rebase")
@changes_context
def _() -> None:
	global SLOT_DIR
	SLOT_DIR = Path(__file__).parent.parent / "Slot_2"
	print("rebased to Slot_2")


@Command("rebase")
@changes_context
def _(r_path: str) -> None:
	global SLOT_DIR
	path = SLOT_DIR.parent / r_path
	if not path.exists():
		print(f"{r_path} does not exist")
		return
	if not path.is_dir():
		print(f"{r_path} is not a directory")
		return
	o = input("Are you sure? (y/n) ").lower()

	if not o or o[0] != "y":
		print("aborted")
		return

	SLOT_DIR = path


def generic_all(pattern:str = "*", *, silent:bool = False) -> None:
	success = 0
	fail = 0
	error = 0
	try:
		for i in SLOT_DIR.glob(pattern):
			print(i.name," "*50,end="\r")
			try:
				out = HASave.load(i)
				out2 = HASave.from_decode(HASave.load(i).encode())
				if out.values != out2.values:
					if not silent:
						print(f"{i.name} failed")
					check(i)
					fail += 1
				else:
					success += 1
			except Exception as e:
				if not silent:
					print(f"{i.name} got an error:")
					print(f'{e.__class__.__name__}:', end="")
					try:
						print(e)
					except UnicodeEncodeError:
						print(repr(str(e))[1:-1])
				error += 1
	except KeyboardInterrupt:
		print("aborted"," "*50)
	else:
		print("done!"," "*50)
	print(f"{success} files passed, {fail} failed, {error} had errors")


@Command("all")
def _() -> None:
	generic_all()


@Command("all")
def _(glob_pattern: str) -> None:
	generic_all(glob_pattern)


@Command("all","silent")
def _() -> None:
	generic_all(silent=True)


@Command("all","silent")
def _(glob_pattern: str) -> None:
	generic_all(glob_pattern,silent=True)


@Command("reload")
def _() -> None:
	load_context()


@Command("encode")
def _(r_path: str) -> None:
	path = SLOT_DIR / r_path
	if not path.exists():
		print(f"{r_path} does not exist")
		return
	if path.is_dir():
		print(f"{r_path} is a directory")
		return
	with path.open("rb") as f:
		r = (HASave.from_decode(bytearray(f.read())).encode())
		display_bin(r)
		print(f"{len(r)} B")


repl_locals = {}


if __name__ == "__main__":
	logging.basicConfig(
		level=logging.DEBUG,filename="viewer.log",filemode="w"
	)
	if prompt_toolkit is not None:
		class Validator(prompt_toolkit.validation.Validator):
			def validate(self, document):
				if document.text == "":
					return
				if prompt_toolkit is None:
					raise RuntimeError()
				if document.text.startswith("@"):
					# command
					b,m = Command.validate(document.text)
					if not b:
						raise prompt_toolkit.validation.ValidationError(
							message=m,
							cursor_position=len(document.text)
						)
					return
				if document.text.startswith("!"):
					return
				elif document.text not in [i.name for i in SLOT_DIR.glob("*")]:
					raise prompt_toolkit.validation.ValidationError(
						message="File not found", cursor_position=len(document.text)
					)

		class Completer(prompt_toolkit.completion.Completer):
			def get_completions(self, document, complete_event):
				if prompt_toolkit is None:
					raise RuntimeError()
				o = [
					*(prompt_toolkit.completion.Completion(
						i.name, start_position=-len(document.text)
					)
					for i in SLOT_DIR.glob("*")
					if i.name.startswith(document.text))
				]
				if document.text.startswith("@") and " " not in document.text:
					o.extend([
						prompt_toolkit.completion.Completion(
							f"@{i.name}", start_position=-len(document.text)
						)
						for i in Command.commands.values()
						if f"@{i.name}".startswith(document.text)
					])

				return o

		session = prompt_toolkit.PromptSession()

		def get_file() -> Path | None:
			if prompt_toolkit is None:
				raise RuntimeError()
			r = session.prompt(
				"> ",
				validator=Validator(),
				completer=Completer(),
				complete_while_typing=True
			)
			if r.startswith("!"):
				try:
					try:
						exec(f"{repl_locals.get('__expr_var','_')} = {r[1:]}",globals(),repl_locals)
					except SyntaxError:
						exec(r[1:],globals(),repl_locals)
					if repl_locals.get('__expr_var',"_") in repl_locals:
						del repl_locals[repl_locals.get('__expr_var',"_")]
				except BaseException as ex:
					print(f'{ex.__class__.__name__}:', ex)
					if repl_locals.get('__expr_var',"_") in repl_locals:
						del repl_locals[repl_locals.get('__expr_var',"_")]
				if repl_locals.get(repl_locals.get('__expr_var',"_")) is not None:
					print(repr(repl_locals.get(repl_locals.get('__expr_var',"_"))))
				return
			if not r.startswith("@"):
				return SLOT_DIR / r
			# execute command
			r = r[1:]
			Command.commands[r.split()[0]].execute(*r.split()[1:])
			return None

	else:
		def get_file() -> Path | None:
			r = input("> ")
			if not r.startswith("@"):
				return SLOT_DIR / r
			# execute command
			r = r[1:]
			if r.split()[0] in Command.commands:
				try:
					Command.commands[r].execute(*r.split()[1:])
				except TypeError as e:
					print(f'{e.__class__.__name__}:', e)
			else:
				print(f"Unknown command: {r}")
			return None
	while True:
		file = get_file()
		if file is None:
			continue
		if file == SLOT_DIR:
			break

		try:
			out = HASave.load(file)
			out2 = HASave.from_decode(HASave.load(file).encode())
		except Exception as e:
			print(f"{file.name} got an error:")
			print(e.__class__.__name__+":",end="")
			try:
				print(e)
			except UnicodeEncodeError:
				print(repr(str(e))[1:-1])
			continue

		if display_mode["dict"] & 1:
			pprint(out.values)
		if display_mode["dict"] == 3:
			print("->")
		if display_mode["dict"] & 2:
			pprint(out2.values)
		check(file)
