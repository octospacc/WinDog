#!/usr/bin/env python3
# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import json, hashlib, re, time, subprocess
from binascii import hexlify
from magic import Magic
from os import listdir
from os.path import isfile
from random import choice, randint
from types import SimpleNamespace
#from traceback import format_exc as TraceText
import mastodon, telegram
from bs4 import BeautifulSoup
from html import unescape as HtmlUnescape
from markdown import markdown
from telegram import Update, ForceReply, Bot
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from urllib import parse as UrlParse
from urllib.request import urlopen, Request

# <https://daringfireball.net/projects/markdown/syntax#backslash>
MdEscapes = '\\`*_{}[]()<>#+-.!|='

Db = {"Chats": {}}
Locale = {"Fallback": {}}

for Dir in ('Lib', 'Mod'):
	for File in listdir(f'./{Dir}WinDog'):
		File = f'./{Dir}WinDog/{File}'
		if isfile(File):
			with open(File, 'r') as File:
				exec(File.read())

Endpoints = {
	"start": cStart,
	"help": cHelp,
	#"config": cConfig,
	"source": cSource,
	"ping": cPing,
	"echo": cEcho,
	"wish": percenter,
	"level": percenter,
	#"hug": multifun,
	#"pat": multifun,
	#"poke": multifun,
	#"cuddle": multifun,
	#"floor": multifun,
	#"hands": multifun,
	#"sessocto": multifun,
	"hash": cHash,
	"eval": cEval,
	#"exec": cExec,
	"format": cFormat,
	"frame": cFrame,
	"web": cWeb,
	"translate": cTranslate,
	"unsplash": cUnsplash,
	"safebooru": cSafebooru,
}

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

def InferMdEscape(Raw:str, Plain:str) -> str:
	Chs = ''
	for Ch in MdEscapes:
		if Ch in Raw and Ch in Plain:
			Chs += Ch
	return Chs

def MarkdownCode(Text:str, Block:bool) -> str:
	return '```\n' + Text.strip().replace('`', '\`') + '\n```'

def MdToTxt(Md:str) -> str:
	return BeautifulSoup(markdown(Md), 'html.parser').get_text(' ')

def HtmlEscapeFull(Raw:str) -> str:
	New = ''
	Hex = hexlify(Raw.encode()).decode()
	for i in range(0, len(Hex), 2):
		New += f'&#x{Hex[i] + Hex[i+1]};'
	return New

def CmdAllowed(update) -> bool:
	if not TGRestrict:
		return True
	else:
		if TGRestrict.lower() == 'whitelist':
			if update.message.chat.id in TGWhitelist:
				return True
	return False

def HandleCmd(update):
	filters(update)
	if CmdAllowed(update):
		return ParseCmd(update.message.text)
	else:
		return False

def GetRawTokens(Text:str) -> list:
	return Text.strip().replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')

def ParseCmd(Msg) -> dict:
	Name = Msg.lower().split(' ')[0][1:].split('@')[0]
	return SimpleNamespace(**{
		"Name": Name,
		"Body": Name.join(Msg.split(Name)[1:]).strip(),
		"Tokens": GetRawTokens(Msg),
		"User": {"Name": "", "Tag": "", "Id": ""},
		"Tagged": {},
	})

def filters(update:Update, context:CallbackContext=None) -> None:
	Cmd = ParseCmd(update.message.text)
	if Cmd.Tokens[0][0] in CmdPrefixes and Cmd.Name in Endpoints:
		Endpoints[Cmd.Name](update, Cmd)
	if Debug and Dumper:
		Text = update.message.text
		Text = (Text.replace('\n', '\\n') if Text else '')
		with open('Dump.txt', 'a') as File:
			File.write(f'[{time.ctime()}] [{int(time.time())}] [{update.message.chat.id}] [{update.message.message_id}] [{update.message.from_user.id}] {Text}\n')
	'''
	if CmdAllowed(update):
		ChatID = update.message.chat.id
		if ChatID in Private['Chats'] and 'Filters' in Private['Chats'][ChatID]:
			for f in Private['Chats'][ChatID]['Filters']:
				if f in update.message.text:
					update.message.reply_text(
						Private['Chats'][ChatID]['Filters'][f],
						reply_to_message_id=update.message.message_id)
	'''

def setfilter(update:Update, context:CallbackContext) -> None:
	pass
	'''
	if CmdAllowed(update):
		ChatID = update.message.chat.id
		if ChatID not in Private['Chats'] or 'Filters' not in Private['Chats'][ChatID]:
			Private['Chats'][ChatID] = {'Filters':{}}
		Private['Chats'][ChatID]['Filters'][update.message.text] = {'Text':0}
	'''

def RandPercent() -> int:
	Num = randint(0,100)
	if Num == 100:
		Num = f'{Num}.00'
	else:
		Num = f'{Num}.{randint(0,9)}{randint(0,9)}'
	return Num

def RandHexStr(Len:int) -> str:
	Hex = ''
	for Char in range(Len):
		Hex += choice('0123456789abcdef')
	return Hex

#def CmdArgs(Msg:str, Cfg:tuple=None):
#	Args = []
#	Msg = Msg.strip().replace('\t', ' ')
#	if Cfg:
#		for i in Cfg:
#			Args += [Msg.replace('  ', ' ').replace('  ', ' ').split(' ')[:i]]
#			Msg = Msg
#	else:
#		return Msg.replace('  ', ' ').replace('  ', ' ').split(' ')

def HttpGet(Url:str):
	return urlopen(Request(Url, headers={"User-Agent": WebUserAgent}))

def SendMsg(Context, Data):
	#Data: Text, Media, Files
	if type(Context) == dict:
		Event = Context['Event'] if 'Event' in Context else None
		Manager = Context['Manager'] if 'Manager' in Context else None
	else:
		[Event, Manager] = [Context, Context]
	if InDict(Data, 'Text'):
		TextPlain = MdToTxt(Data['Text'])
		TextMarkdown = CharEscape(HtmlUnescape(Data['Text']), InferMdEscape(HtmlUnescape(Data['Text']), TextPlain))
	if isinstance(Manager, mastodon.Mastodon):
		if InDict(Data, 'Media'):
			Media = Manager.media_post(Data['Media'], Magic(mime=True).from_buffer(Data['Media']))
			while Media['url'] == 'null':
				Media = Manager.media(Media)
		if InDict(Data, 'Text'):
			Manager.status_post(
				status=(TextPlain + '\n\n@' + Event['account']['acct']),
				media_ids=(Media if InDict(Data, 'Media') else None),
				in_reply_to_id=Event['status']['id'],
				visibility=('direct' if Event['status']['visibility'] == 'direct' else 'unlisted'),
			)
	elif isinstance(Manager, telegram.Update):
		if InDict(Data, 'Media'):
			Event.message.reply_photo(
				Data['Media'],
				caption=(TextMarkdown if InDict(Data, 'Text') else None),
				parse_mode='MarkdownV2',
				reply_to_message_id=Event.message.message_id,
			)
		elif InDict(Data, 'Text'):
			Event.message.reply_markdown_v2(
				TextMarkdown,
				reply_to_message_id=Event.message.message_id,
			)

def Main() -> None:
	SetupDb()
	SetupLocale()

	#Private['Chats'].update({update.message.chat.id:{}})

	updater = Updater(TGToken)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('config', cConfig))
	#dispatcher.add_handler(CommandHandler('time', cTime))
	dispatcher.add_handler(CommandHandler('exec', cExec))

	for Cmd in ('hug', 'pat', 'poke', 'cuddle', 'floor', 'hands', 'sessocto'):
		dispatcher.add_handler(CommandHandler(Cmd, multifun))

	#dispatcher.add_handler(CommandHandler('setfilter', setfilter))
	dispatcher.add_handler(MessageHandler(Filters.text | Filters.command, filters))

	print('Starting WinDog...')
	updater.start_polling()

	if MastodonUrl and MastodonToken:
		Mastodon = mastodon.Mastodon(api_base_url=MastodonUrl, access_token=MastodonToken)
		class MastodonListener(mastodon.StreamListener):
			def on_notification(self, Event):
				if Event['type'] == 'mention':
					Msg = BeautifulSoup(Event['status']['content'], 'html.parser').get_text(' ').strip().replace('\t', ' ')
					if not Msg.split('@')[0]:
						Msg = ' '.join('@'.join(Msg.split('@')[1:]).strip().split(' ')[1:]).strip()
					if Msg[0] in CmdPrefixes:
						Cmd = ParseCmd(Msg)
						if Cmd.Name in Endpoints:
							Endpoints[Cmd.Name]({"Event": Event, "Manager": Mastodon}, Cmd)
		Mastodon.stream_user(MastodonListener())

	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	try:
		from Config import *
	except Exception:
		pass

	Main()
	print('Closing WinDog...')
