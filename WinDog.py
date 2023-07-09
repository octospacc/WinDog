#!/usr/bin/env python3
# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import json, hashlib, re, time, subprocess
from os import listdir
from os.path import isfile
from random import choice, randint
from types import SimpleNamespace
#from traceback import format_exc as TraceText
import mastodon, telegram
from bs4 import BeautifulSoup
from telegram import Update, ForceReply, Bot
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from urllib import parse as UrlParse
from urllib.request import urlopen, Request

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
	"echo": cEcho,
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

def MarkdownCode(Text:str, Block:bool):
	return '```\n' + CharEscape(Text.strip(), 'MARKDOWN') + '\n```'

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
	})

def filters(update:Update, context:CallbackContext=None) -> None:
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
		Num = str(Num) + '\.00'
	else:
		Num = str(Num) + '\.' + str(randint(0,9)) + str(randint(0,9))
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
	if isinstance(Manager, mastodon.Mastodon):
		Manager.status_post(
			(Data['Text'] + '\n\n@' + Event['account']['acct']),
			in_reply_to_id=Event['status']['id'],
			visibility=('direct' if Event['status']['visibility'] == 'direct' else 'unlisted')
		)
	elif isinstance(Manager, telegram.Update):
		Event.message.reply_markdown_v2(
			Data['Text'],
			reply_to_message_id=Event.message.message_id
		)

def Main() -> None:
	SetupDb()
	SetupLocale()

	#Private['Chats'].update({update.message.chat.id:{}})

	updater = Updater(TGToken)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('start', cStart))
	dispatcher.add_handler(CommandHandler('config', cConfig))
	dispatcher.add_handler(CommandHandler('help', cHelp))
	dispatcher.add_handler(CommandHandler('source', cSource))
	dispatcher.add_handler(CommandHandler('echo', cEcho2))
	dispatcher.add_handler(CommandHandler('ping', cPing))
	#dispatcher.add_handler(CommandHandler('time', cTime))
	dispatcher.add_handler(CommandHandler('hash', cHash))
	dispatcher.add_handler(CommandHandler('eval', cEval))
	dispatcher.add_handler(CommandHandler('exec', cExec))
	dispatcher.add_handler(CommandHandler('web', cWeb))
	dispatcher.add_handler(CommandHandler('unsplash', cUnsplash))
	dispatcher.add_handler(CommandHandler('safebooru', cSafebooru))

	for Cmd in ('wish', 'level'):
		dispatcher.add_handler(CommandHandler(Cmd, percenter))
	for Cmd in ('hug', 'pat', 'poke', 'cuddle', 'floor', 'hands', 'sessocto'):
		dispatcher.add_handler(CommandHandler(Cmd, multifun))

	#dispatcher.add_handler(CommandHandler('setfilter', setfilter))
	dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, filters))

	print('Starting WinDog...')
	updater.start_polling()

	#if MastodonUrl and MastodonToken:
	Mastodon = mastodon.Mastodon(api_base_url=MastodonUrl, access_token=MastodonToken)
	class mmyListener(mastodon.StreamListener):
		def on_notification(self, Event):
			if Event['type'] == 'mention':
				Msg = BeautifulSoup(Event['status']['content'], 'html.parser').get_text(' ').strip().replace('\t', ' ')
				if not Msg.split('@')[0]:
					Msg = ' '.join('@'.join(Msg.split('@')[1:]).strip().split(' ')[1:]).strip()
				if Msg[0] in '.!/':
					Cmd = ParseCmd(Msg)
					if Cmd.Name in Endpoints:
						Endpoints[Cmd.Name]({"Event": Event, "Manager": Mastodon}, Cmd)
					
	Mastodon.stream_user(mmyListener())

	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	try:
		from Config import *
	except Exception:
		pass

	Main()
	print('Closing WinDog...')
