#!/usr/bin/env python3
# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import json, time
from binascii import hexlify
from glob import glob
from hashlib import new as hashlib_new
from html import escape as html_escape, unescape as html_unescape
from os import listdir
from os.path import isfile, isdir
from random import choice, choice as randchoice, randint
from threading import Thread
from traceback import format_exc
from urllib import parse as urlparse
from yaml import load as yaml_load, BaseLoader as yaml_BaseLoader
from bs4 import BeautifulSoup
from markdown import markdown
from LibWinDog.Types import *
from LibWinDog.Config import *
from LibWinDog.Database import *

# <https://daringfireball.net/projects/markdown/syntax#backslash>
MdEscapes = '\\`*_{}[]()<>#+-.!|='

def NamespaceUnion(namespaces:list|tuple, clazz=SimpleNamespace):
	dikt = {}
	for namespace in namespaces:
		for key, value in tuple(namespace.__dict__.items()):
			dikt[key] = value
	return clazz(**dikt)

def Log(text:str, level:str="?", *, newline:bool|None=None, inline:bool=False) -> None:
	endline = '\n'
	if newline == False or (inline and newline == None):
		endline = ''
	text = (text if inline else f"[{level}] [{time.ctime()}] [{int(time.time())}] {text}")
	if LogToConsole:
		print(text, end=endline)
	if LogToFile:
		open("./Log.txt", 'a').write(text + endline)

def SetupLocales() -> None:
	global Locale
	for file in listdir('./Locale'):
		lang = file.split('.')[0]
		try:
			with open(f'./Locale/{file}') as file:
				Locale[lang] = json.load(file)
		except Exception:
			Log(f'Cannot load {lang} locale, exiting.')
			raise
			exit(1)
	for key in Locale[DefaultLang]:
		Locale['Fallback'][key] = Locale[DefaultLang][key]
	for lang in Locale:
		for key in Locale[lang]:
			if not key in Locale['Fallback']:
				Locale['Fallback'][key] = Locale[lang][key]
	def querier(query:str, lang:str=DefaultLang):
		value = None
		query = query.split('.')
		try:
			value = Locale.Locale[lang]
			for key in query:
				value = value[key]
		except Exception:
			value = Locale.Locale['Fallback']
			for key in query:
				value = value[key]
		return value
	Locale['__'] = querier
	Locale['Locale'] = Locale
	Locale = SimpleNamespace(**Locale)

def SureArray(array:any) -> list|tuple:
	return (array if type(array) in [list, tuple] else [array])

def InDict(dikt:dict, key:str, /) -> any:
	return (dikt[key] if key in dikt else None)

def DictGet(dikt:dict, key:str, /) -> any:
	return (dikt[key] if key in dikt else None)

def ObjGet(node:object, query:str, /) -> any:
	for key in query.split('.'):
		if hasattr(node, "__getitem__") and node.__getitem__:
			# dicts and such
			method = "__getitem__"
			exception = KeyError
		else:
			# namespaces and such
			method = "__getattribute__"
			exception = AttributeError
		try:
			node = node.__getattribute__(method)(key)
		except exception:
			return None
	return node

def isinstanceSafe(clazz:any, instance:any, /) -> bool:
	if instance != None:
		return isinstance(clazz, instance)
	return False

def get_string(bank:dict, query:str|dict, lang:str=None, /):
	if not (result := ObjGet(bank, f"{query}.{lang or DefaultLang}")):
		if not (result := ObjGet(bank, f"{query}.en")):
			result = ObjGet(bank, query)
	return result

def strip_url_scheme(url:str) -> str:
	tokens = urlparse.urlparse(url)
	return f"{tokens.netloc}{tokens.path}"

def CharEscape(String:str, Escape:str='') -> str:
	if Escape == 'MARKDOWN':
		return escape_markdown(String, version=2)
	else:
		if Escape == 'MARKDOWN_SPEECH':
			Escape = '+-_.!()[]{}<>'
		elif Escape == 'MARKDOWN_SPEECH_FORMAT':
			Escape = '+-_.!()[]<>'
		for c in Escape:
			String = String.replace(c, '\\'+c)
	return String

def InferMdEscape(raw:str, plain:str) -> str:
	chars = ''
	for char in MdEscapes:
		if char in raw and char in plain:
			chars += char
	return chars

def MdToTxt(md:str) -> str:
	return BeautifulSoup(markdown(md), 'html.parser').get_text(' ')

def HtmlEscapeFull(Raw:str) -> str:
	New = ''
	Hex = hexlify(Raw.encode()).decode()
	for i in range(0, len(Hex), 2):
		New += f'&#x{Hex[i] + Hex[i+1]};'
	return New

def GetWeightedText(*texts) -> str|None:
	for text in texts:
		if text:
			return text

def RandPercent() -> int:
	num = randint(0,100)
	return (f'{num}.00' if num == 100 else f'{num}.{randint(0,9)}{randint(0,9)}')

def RandHexStr(length:int) -> str:
	hexa = ''
	for char in range(length):
		hexa += choice('0123456789abcdef')
	return hexa

def GetUserSettings(user_id:str) -> SafeNamespace|None:
	try:
		return SafeNamespace(**EntitySettings.select().join(User).where(User.id == user_id).dicts().get())
	except EntitySettings.DoesNotExist:
		return None

# TODO ignore tagged commands when they are not directed to the bot's username
def ParseCommand(text:str) -> SafeNamespace|None:
	if not text:
		return None
	text = text.strip()
	try: # ensure text is a non-empty command
		if not (text[0] in CmdPrefixes and text[1:].strip()):
			return None
	except IndexError:
		return None
	command = SafeNamespace()
	command.tokens = text.split()
	command.name = command.tokens[0][1:].lower().split('@')[0]
	command.body = text[len(command.tokens[0]):].strip()
	if command.name not in Endpoints:
		return command
	if (endpoint_arguments := Endpoints[command.name].arguments):#["arguments"]):
		command.arguments = {}
		index = 1
		for key in endpoint_arguments:
			if not endpoint_arguments[key]:
				continue # skip optional (False) arguments for now, they will be implemented later
			try:
				value = command.tokens[index]
				command.body = command.body[len(value):].strip()
			except IndexError:
				value = None
			command.arguments[key] = value
			index += 1
	return command

def OnMessageParsed(data:InputMessageData) -> None:
	DumpMessage(data)
	UpdateUserDb(data.user)

def UpdateUserDb(user:SafeNamespace) -> None:
	try:
		User.get(User.id == user.id)
	except User.DoesNotExist:
		user_hash = ("sha256:" + hashlib_new("sha256", user.id.encode()).hexdigest())
		try:
			User.get(User.id_hash == user_hash)
			User.update(id=user.id).where(User.id_hash == user_hash).execute()
		except User.DoesNotExist:
			User.create(id=user.id, id_hash=user_hash)

def DumpMessage(data:InputMessageData) -> None:
	if not (Debug and (DumpToFile or DumpToConsole)):
		return
	text = (data.text_plain.replace('\n', '\\n') if data.text_auto else '')
	text = f"[{int(time.time())}] [{time.ctime()}] [{data.room and data.room.id}] [{data.message_id}] [{data.user.id}] {text}"
	if DumpToConsole:
		print(text, data)
	if DumpToFile:
		open((DumpToFile if (DumpToFile and type(DumpToFile) == str) else "./Dump.txt"), 'a').write(text + '\n')

def SendMessage(context:EventContext, data:OutputMessageData, destination=None) -> None:
	data = (OutputMessageData(**data) if type(data) == dict else data)

	# TODO remove this after all modules are changed
	if data.Text and not data.text:
		data.text = data.Text
	if data.TextPlain and not data.text_plain:
		data.text_plain = data.TextPlain
	if data.TextMarkdown and not data.text_markdown:
		data.text_markdown = data.TextMarkdown

	if data.text_plain or data.text_markdown or data.text_html:
		if data.text_html and not data.text_plain:
			data.text_plain = BeautifulSoup(data.text_html, "html.parser").get_text()
		elif data.text_markdown and not data.text_plain:
			data.text_plain = data.text_markdown
	elif data.text:
		# our old system attempts to always receive Markdown and retransform when needed
		data.text_plain = MdToTxt(data.text)
		data.text_markdown = CharEscape(html_unescape(data.text), InferMdEscape(html_unescape(data.text), data.text_plain))
		#data.text_html = ???
	if data.media:
		data.media = SureArray(data.media)
	#for platform in Platforms.values():
	#	if isinstanceSafe(context.event, platform.eventClass) or isinstanceSafe(context.manager, platform.managerClass):
	#		return platform.sender(context, data, destination)
	return Platforms[context.platform].sender(context, data, destination)

def SendNotice(context:EventContext, data) -> None:
	pass

def DeleteMessage(context:EventContext, data) -> None:
	pass

def RegisterPlatform(name:str, main:callable, sender:callable, linker:callable=None, *, eventClass=None, managerClass=None) -> None:
	Platforms[name.lower()] = SafeNamespace(main=main, sender=sender, linker=linker, eventClass=eventClass, managerClass=managerClass)
	Log(f"{name}, ", inline=True)

def RegisterModule(name:str, endpoints:dict, *, group:str|None=None) -> None:
	module = SafeNamespace(group=group, endpoints=endpoints, get_string=(lambda query, lang=None, /: None))
	if isfile(file := f"./ModWinDog/{name}/{name}.yaml"):
		module.strings = yaml_load(open(file, 'r').read().replace("\t", "    "), Loader=yaml_BaseLoader)
		module.get_string = (lambda query, lang=None: get_string(module.strings, query, lang))
	Modules[name] = module
	Log(f"{name}, ", inline=True)
	for endpoint in endpoints:
		endpoint.module = module
		for name in endpoint.names:
			Endpoints[name] = endpoint

def CallEndpoint(name:str, context:EventContext, data:InputMessageData):
	endpoint = Endpoints[name]
	context.endpoint = endpoint
	context.module = endpoint.module
	context.endpoint.get_string = (lambda query, lang=None, /: endpoint.module.get_string(f"endpoints.{data.command.name}.{query}", lang))
	return endpoint.handler(context, data)

def WriteNewConfig() -> None:
	Log("💾️ No configuration found! Generating and writing to `./Config.py`... ", inline=True)
	with open("./Config.py", 'w') as configFile:
		opening = '# windog config start #'
		closing = '# end windog config #'
		for folder in ("LibWinDog", "ModWinDog"):
			for file in glob(f"./{folder}/**/*.py", recursive=True):
				try:
					name = '/'.join(file.split('/')[1:-1])
					heading = f"# ==={'=' * len(name)}=== #"
					source = open(file, 'r').read().replace(f"''' {opening}", f'""" {opening}').replace(f"{closing} '''", f'{closing} """')
					content = '\n'.join(content.split(f'""" {opening}')[1].split(f'{closing} """')[0].split('\n')[1:-1])
					configFile.write(f"{heading}\n# 🔽️ {name} 🔽️ #\n{heading}\n{content}\n\n")
				except IndexError:
					pass

def Main() -> None:
	#SetupDb()
	SetupLocales()
	Log(f"📨️ Initializing Platforms... ", newline=False)
	for platform in Platforms:
		if Platforms[platform].main():
			Log(f"{platform}, ", inline=True)
	Log("...Done. ✅️", inline=True, newline=True)
	Log("🐶️ WinDog Ready!")
	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	Log("🌞️ WinDog Starting...")
	Locale = {"Fallback": {}}
	Platforms, Modules, ModuleGroups, Endpoints = {}, {}, {}, {}

	for folder in ("LibWinDog/Platforms", "ModWinDog"):
		match folder:
			case "LibWinDog/Platforms":
				Log("📩️ Loading Platforms... ", newline=False)
			case "ModWinDog":
				Log("🔩️ Loading Modules... ", newline=False)
		for name in listdir(f"./{folder}"):
			path = f"./{folder}/{name}"
			if isfile(path):
				exec(open(path, 'r').read())
			elif isdir(path):
				files = listdir(path)
				if f"{name}.py" in files:
					files.remove(f"{name}.py")
					exec(open(f"{path}/{name}.py", 'r').read())
				for file in files:
					if file.endswith(".py"):
						exec(open(f"{path}/{name}.py", 'r').read())
				# TODO load locales
				#for name in listdir(path):
				#	if name.lower().endswith('.json'):
				#		
		Log("...Done. ✅️", inline=True, newline=True)

	Log("💽️ Loading Configuration... ", newline=False)
	from Config import *
	if isfile("./Config.py"):
		from Config import *
	else:
		WriteNewConfig()
	Log("Done. ✅️", inline=True, newline=True)

	Main()
	Log("🌚️ WinDog Stopping...")

