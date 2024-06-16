#!/usr/bin/env python3
# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import json, time
from binascii import hexlify
from magic import Magic
from os import listdir
from os.path import isfile, isdir
from random import choice, randint
from types import SimpleNamespace
from traceback import format_exc
from bs4 import BeautifulSoup
from html import unescape as HtmlUnescape
from markdown import markdown
from LibWinDog.Database import *

# <https://daringfireball.net/projects/markdown/syntax#backslash>
MdEscapes = '\\`*_{}[]()<>#+-.!|='

def Log(text:str, level:str="?", *, newline:bool|None=None, inline:bool=False) -> None:
	endline = '\n'
	if newline == False or (inline and newline == None):
		endline = ''
	print((text if inline else f"[{level}] [{int(time.time())}] {text}"), end=endline)

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

def InDict(Dict:dict, Key:str) -> any:
	if Key in Dict:
		return Dict[Key]
	else:
		return None

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

def ParseCmd(msg) -> dict|None:
	name = msg.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')[0][1:].split('@')[0]
	if not name: return
	return SimpleNamespace(**{
		"Name": name.lower(),
		"Body": name.join(msg.split(name)[1:]).strip(),
		"Tokens": GetRawTokens(msg),
		"User": None,
		"Quoted": None,
	})

def GetWeightedText(texts:tuple) -> str|None:
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

def OnMessageReceived() -> None:
	pass

def SendMsg(context, data, destination=None) -> None:
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

def RegisterPlatform(name:str, main:callable, sender:callable, *, eventClass=None, managerClass=None) -> None:
	Platforms[name] = {"main": main, "sender": sender, "eventClass": eventClass, "managerClass": managerClass}
	Log(f"{name}, ", inline=True)

def RegisterModule(name:str, endpoints:dict, *, group:str|None=None, summary:str|None=None) -> None:
	Modules[name] = {"group": group, "summary": summary, "endpoints": endpoints}
	Log(f"{name}, ", inline=True)
	for endpoint in endpoints:
		endpoint = endpoints[endpoint]
		for name in endpoint["names"]:
			Endpoints[name] = endpoint["handler"]

def CreateEndpoint(names:list[str], handler:callable, arguments:dict[str, dict]={}, *, summary:str|None=None) -> dict:
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

	for dir in ("LibWinDog/Platforms", "ModWinDog"):
		match dir:
			case "LibWinDog/Platforms":
				Log("📩️ Loading Platforms... ", newline=False)
			case "ModWinDog":
				Log("🔩️ Loading Modules... ", newline=False)
		for name in listdir(f"./{dir}"):
			path = f"./{dir}/{name}"
			if isfile(path):
				exec(open(path, 'r').read())
			elif isdir(path):
				exec(open(f"{path}/{name}.py", 'r').read())
				# TODO load locales
				#for name in listdir(path):
				#	if name.lower().endswith('.json'):
				#		
		Log("...Done. ✅️", inline=True, newline=True)

	Log("💽️ Loading Configuration", newline=False)
	exec(open("./LibWinDog/Config.py", 'r').read())
	try:
		from Config import *
	except Exception:
		Log(format_exc())
	Log("...Done. ✅️", inline=True, newline=True)

	Main()
	Log("🌚️ WinDog Stopping...")

