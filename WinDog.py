#!/usr/bin/env python3
# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import json, time
from binascii import hexlify
from glob import glob
from magic import Magic
from os import listdir
from os.path import isfile, isdir
from random import choice, randint
from types import SimpleNamespace
from traceback import format_exc
from bs4 import BeautifulSoup
from html import unescape as HtmlUnescape
from markdown import markdown
from LibWinDog.Config import *
from LibWinDog.Database import *

# <https://daringfireball.net/projects/markdown/syntax#backslash>
MdEscapes = '\\`*_{}[]()<>#+-.!|='

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

def isinstanceSafe(clazz:any, instance:any) -> bool:
	if instance != None:
		return isinstance(clazz, instance)
	return False

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

def MarkdownCode(text:str, block:bool) -> str:
	return ('```\n' + text.strip().replace('`', '\`') + '\n```')

def MdToTxt(md:str) -> str:
	return BeautifulSoup(markdown(md), 'html.parser').get_text(' ')

def HtmlEscapeFull(Raw:str) -> str:
	New = ''
	Hex = hexlify(Raw.encode()).decode()
	for i in range(0, len(Hex), 2):
		New += f'&#x{Hex[i] + Hex[i+1]};'
	return New

def GetRawTokens(text:str) -> list:
	return text.strip().replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')

def ParseCmd(msg) -> SimpleNamespace|None:
	#if not len(msg) or msg[1] not in CmdPrefixes:
	#	return
	name = msg.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')[0][1:].split('@')[0]
	#if not name:
	#	return
	return SimpleNamespace(**{
		"Name": name.lower(),
		"Body": name.join(msg.split(name)[1:]).strip(),
		"Tokens": GetRawTokens(msg),
		"User": None,
		"Quoted": None,
	})

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

def ParseCommand(text:str) -> SimpleNamespace|None:
	text = text.strip()
	try: # ensure command is not empty
		if not (text[0] in CmdPrefixes and text[1:].strip()):
			return
	except IndexError:
		return
	command = SimpleNamespace(**{})
	command.tokens = text.replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("  ", " ").replace("  ", " ").split(" ")
	command.name = command.tokens[0][1:].lower()
	command.body = text[len(command.tokens[0]):].strip()
	if (endpoint_arguments := Endpoints[command.name]["arguments"]):
		command.arguments = {}
		# TODO differences between required (True) and optional (False) args
		for index, key in enumerate(endpoint_arguments):
			try:
				value = command.tokens[index + 1]
				command.body = command.body[len(value):].strip()
			except IndexError:
				value = None
			command.arguments[key] = value
	return command

def OnMessageParsed(data:SimpleNamespace) -> None:
	if Debug and (DumpToFile or DumpToConsole):
		text = (data.text_auto.replace('\n', '\\n') if data.text_auto else '')
		text = f"[{int(time.time())}] [{time.ctime()}] [{data.room_id}] [{data.message_id}] [{data.user.id}] {text}"
		if DumpToConsole:
			print(text)
		if DumpToFile:
			open((DumpToFile if (DumpToFile and type(DumpToFile) == str) else "./Dump.txt"), 'a').write(text + '\n')

def SendMsg(context, data, destination=None) -> None:
	return SendMessage(context, data, destination)

def SendMessage(context, data, destination=None) -> None:
	if type(context) == dict:
		event = context['Event'] if 'Event' in context else None
		manager = context['Manager'] if 'Manager' in context else None
	else:
		[event, manager] = [context, context]
	if InDict(data, 'TextPlain') or InDict(data, 'TextMarkdown'):
		textPlain = InDict(data, 'TextPlain')
		textMarkdown = InDict(data, 'TextMarkdown')
		if not textPlain:
			textPlain = textMarkdown
	elif InDict(data, 'Text'):
		# our old system attempts to always receive Markdown and retransform when needed
		textPlain = MdToTxt(data['Text'])
		textMarkdown = CharEscape(HtmlUnescape(data['Text']), InferMdEscape(HtmlUnescape(data['Text']), textPlain))
	for platform in Platforms:
		platform = Platforms[platform]
		if isinstanceSafe(event, InDict(platform, "eventClass")) or isinstanceSafe(manager, InDict(platform, "managerClass")):
			platform["sender"](event, manager, data, destination, textPlain, textMarkdown)

def SendReaction() -> None:
	pass

def RegisterPlatform(name:str, main:callable, sender:callable, *, eventClass=None, managerClass=None) -> None:
	Platforms[name] = {"main": main, "sender": sender, "eventClass": eventClass, "managerClass": managerClass}
	Log(f"{name}, ", inline=True)

def RegisterModule(name:str, endpoints:dict, *, group:str|None=None, summary:str|None=None) -> None:
	Modules[name] = {"group": group, "summary": summary, "endpoints": endpoints}
	Log(f"{name}, ", inline=True)
	for endpoint in endpoints:
		endpoint = endpoints[endpoint]
		for name in endpoint["names"]:
			Endpoints[name] = endpoint

# TODO register endpoint with this instead of RegisterModule
def CreateEndpoint(names:list[str], handler:callable, arguments:dict[str, bool]|None=None, *, summary:str|None=None) -> dict:
	return {"names": names, "summary": summary, "handler": handler, "arguments": arguments}

def Main() -> None:
	#SetupDb()
	SetupLocales()
	Log(f"📨️ Initializing Platforms... ", newline=False)
	for platform in Platforms:
		if Platforms[platform]["main"]():
			Log(f"{platform}, ", inline=True)
	Log("...Done. ✅️", inline=True, newline=True)
	Log("🐶️ WinDog Ready!")
	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	Log("🌞️ WinDog Starting...")
	#Db = {"Rooms": {}, "Users": {}}
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
	#exec(open("./LibWinDog/Config.py", 'r').read())
	from Config import *
	if isfile("./Config.py"):
		from Config import *
	else:
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
	Log("Done. ✅️", inline=True, newline=True)

	Main()
	Log("🌚️ WinDog Stopping...")

