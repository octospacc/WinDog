#!/usr/bin/env python3
# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import json, re, time, subprocess
from binascii import hexlify
from magic import Magic
from os import listdir
from os.path import isfile, isdir
from random import choice, randint
from types import SimpleNamespace
#from traceback import format_exc as TraceText
from bs4 import BeautifulSoup
from html import unescape as HtmlUnescape
from markdown import markdown

# <https://daringfireball.net/projects/markdown/syntax#backslash>
MdEscapes = '\\`*_{}[]()<>#+-.!|='

Db = {"Rooms": {}, "Users": {}}
Locale = {"Fallback": {}}
Platforms = {}
Commands = {}

for dir in ("LibWinDog/Platforms", "ModWinDog"):
	for path in listdir(f"./{dir}"):
		path = f"./{dir}/{path}"
		if isfile(path):
			exec(open(path, 'r').read())
		elif isdir(path):
			exec(open(f"{path}/mod.py", 'r').read())
exec(open("./LibWinDog/Config.py", 'r').read())

def SetupLocale() -> None:
	global Locale
	for File in listdir('./Locale'):
		Lang = File.split('.')[0]
		try:
			with open(f'./Locale/{File}') as File:
				Locale[Lang] = json.load(File)
		except Exception:
			print(f'Cannot load {Lang} locale, exiting.')
			raise
			exit(1)
	for Key in Locale[DefaultLang]:
		Locale['Fallback'][Key] = Locale[DefaultLang][Key]
	for Lang in Locale:
		for Key in Locale[Lang]:
			if not Key in Locale['Fallback']:
				Locale['Fallback'][Key] = Locale[Lang][Key]
	def __(Key:str, Lang:str=DefaultLang):
		Set = None
		Key = Key.split('.')
		try:
			Set = Locale.Locale[Lang]
			for El in Key:
				Set = Set[El]
		except Exception:
			Set = Locale.Locale['Fallback']
			for El in Key:
				Set = Set[El]
		return Set
	Locale['__'] = __
	Locale['Locale'] = Locale
	Locale = SimpleNamespace(**Locale)

def SetupDb() -> None:
	global Db
	try:
		with open('Database.json', 'r') as File:
			Db = json.load(File)
	except Exception:
		pass

def InDict(Dict:dict, Key:str):
	if Key in Dict:
		return Dict[Key]
	else:
		return None

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
	return '```\n' + text.strip().replace('`', '\`') + '\n```'

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
	name = msg.lower().split(' ')[0][1:].split('@')[0]
	if not name:
		return
	return SimpleNamespace(**{
		"Name": name,
		"Body": name.join(msg.split(name)[1:]).strip(),
		"Tokens": GetRawTokens(msg),
		"User": None,
		"Quoted": None,
	})

def GetWeightedText(texts:tuple) -> str:
	for text in texts:
		if text:
			return text

def RandPercent() -> int:
	num = randint(0,100)
	return (f'{num}.00' if num == 100 else f'{num}.{randint(0,9)}{randint(0,9)}')

def RandHexStr(Len:int) -> str:
	Hex = ''
	for Char in range(Len):
		Hex += choice('0123456789abcdef')
	return Hex

def SendMsg(Context, Data, Destination=None) -> None:
	if type(Context) == dict:
		Event = Context['Event'] if 'Event' in Context else None
		Manager = Context['Manager'] if 'Manager' in Context else None
	else:
		[Event, Manager] = [Context, Context]
	if InDict(Data, 'TextPlain') or InDict(Data, 'TextMarkdown'):
		TextPlain = InDict(Data, 'TextPlain')
		TextMarkdown = InDict(Data, 'TextMarkdown')
		if not TextPlain:
			TextPlain = TextMarkdown
	elif InDict(Data, 'Text'):
		# our old system attemps to always receive Markdown and retransform when needed
		TextPlain = MdToTxt(Data['Text'])
		TextMarkdown = CharEscape(HtmlUnescape(Data['Text']), InferMdEscape(HtmlUnescape(Data['Text']), TextPlain))
	for platform in Platforms:
		platform = Platforms[platform]
		if ("eventClass" in platform and isinstance(Event, platform["eventClass"])) \
		or ("managerClass" in platform and isinstance(Manager, platform["managerClass"])):
			platform["sender"](Event, Manager, Data, Destination, TextPlain, TextMarkdown)

def Main() -> None:
	SetupDb()
	SetupLocale()
	TelegramMain()
	MastodonMain()
	#MatrixMain()
	#for platform in Platforms:
	#	Platforms[platform]["main"]()
	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	try:
		from Config import *
	except Exception:
		pass
	print('Starting WinDog...')
	Main()
	print('Closing WinDog...')

