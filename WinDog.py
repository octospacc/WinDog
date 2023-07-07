#!/usr/bin/env python3

# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import json, hashlib, re, time, subprocess
from os import listdir
from random import choice, randint
from types import SimpleNamespace
from telegram import Update, ForceReply, Bot
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from Config import *

Db = {"Chats": {}}
Locale = {"Fallback": {}}

def SetupDb() -> None:
	global Db
	try:
		with open('Database.json', 'r') as File:
			Db = json.load(File)
	except Exception:
		pass

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

def CharEscape(String, Escape='') -> str:
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

def GetRawTokens(Text:str) -> list:
	return Text.strip().replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')

def CmdFilter(Msg) -> str:
	return Msg.lower().split(' ')[0][1:].split('@')[0]

def RandPercent() -> int:
	Num = randint(0,100)
	if Num == 100:
		Num = str(Num) + '\.00'
	else:
		Num = str(Num) + '\.' + str(randint(0,9)) + str(randint(0,9))
	return Num

def cStart(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		user = update.effective_user
		update.message.reply_markdown_v2(
			CharEscape(choice(Locale.__('start')), 'MARKDOWN_SPEECH').format(user.mention_markdown_v2()),
			reply_to_message_id=update.message.message_id)

def cHelp(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		update.message.reply_markdown_v2(
			CharEscape(choice(Locale.__('help')), 'MARKDOWN_SPEECH'),
			reply_to_message_id=update.message.message_id)

def cConfig(update:Update, context:CallbackContext) -> None:
	pass

def cEcho(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Msg = update.message.text
		if len(Msg.split(' ')) >= 2:
			Text = Msg[len(Msg.split(' ')[0])+1:]
			update.message.reply_text(
				Text,
				reply_to_message_id=update.message.message_id)
		else:
			Text = CharEscape(choice(Locale.__('echo.empty')), '.!')
			update.message.reply_markdown_v2(
				Text,
				reply_to_message_id=update.message.message_id)

def cPing(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		update.message.reply_markdown_v2(
			'*Pong\!*',
			reply_to_message_id=update.message.message_id)

def percenter(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Msg = update.message.text
		Key = CmdFilter(Msg)
		Toks = GetRawTokens(Msg)
		Thing = Key.join(Msg.split(Key)[1:]).strip()
		if len(Toks) >= 2:
			Text = choice(Locale.__(f'{Key}.done'))
		else:
			Text = choice(Locale.__(f'{Key}.empty'))
		update.message.reply_markdown_v2(
			CharEscape(Text, '.!').format(Cmd=Toks[0], Percent=RandPercent(), Thing=Thing),
			reply_to_message_id=update.message.message_id)

def multifun(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Key = CmdFilter(update.message.text)
		ReplyToMsg = update.message.message_id
		if update.message.reply_to_message:
			ReplyFromUID = update.message.reply_to_message.from_user.id
			if ReplyFromUID == TGID and 'bot' in Locale.__(Key):
				Text = CharEscape(choice(Locale.__(f'{Key}.bot')), 'MARKDOWN_SPEECH')
			elif ReplyFromUID == update.message.from_user.id and 'self' in Locale.__(Key):
				FromUName = CharEscape(update.message.from_user.first_name, 'MARKDOWN')
				Text = CharEscape(choice(Locale.__(f'{Key}.self')), 'MARKDOWN_SPEECH').format(FromUName)
			else:
				if 'others' in Locale.__(Key):
					FromUName = CharEscape(update.message.from_user.first_name, 'MARKDOWN')
					ToUName = CharEscape(update.message.reply_to_message.from_user.first_name, 'MARKDOWN')
					Text = CharEscape(choice(Locale.__(f'{Key}.others')), 'MARKDOWN_SPEECH').format(FromUName,ToUName)
					ReplyToMsg = update.message.reply_to_message.message_id
		else:
			if 'empty' in Locale.__(Key):
				Text = CharEscape(choice(Locale.__(f'{Key}.empty')), 'MARKDOWN_SPEECH')
		update.message.reply_markdown_v2(Text, reply_to_message_id=ReplyToMsg)

def cUnsplash(update:Update, context:CallbackContext) -> None:
	pass

def filters(update:Update, context:CallbackContext) -> None:
	if Debug and Dumper:
		with open('Dump.txt', 'a') as File:
			File.write(f'[{time.ctime()}] [{int(time.time())}] [{update.message.chat.id}] [{update.message.message_id}] [{update.message.from_user.id}] {update.message.text}\n')
	'''
	if CmdRestrict(update):
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
	if CmdRestrict(update):
		ChatID = update.message.chat.id
		if ChatID not in Private['Chats'] or 'Filters' not in Private['Chats'][ChatID]:
			Private['Chats'][ChatID] = {'Filters':{}}
		Private['Chats'][ChatID]['Filters'][update.message.text] = {'Text':0}
	'''

def cTime(update:Update, context:CallbackContext) -> None:
	update.message.reply_markdown_v2(
		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
		reply_to_message_id=update.message.message_id)

def cHash(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Msg = update.message.text
		Toks = GetRawTokens(Msg)
		if len(Toks) >= 3 and Toks[1] in hashlib.algorithms_available:
			Alg = Toks[1]
			Caption = hashlib.new(Alg, Alg.join(Msg.split(Alg)[1:]).strip().encode()).hexdigest()
		else:
			Caption = CharEscape(choice(Locale.__('hash')).format(Toks[0], hashlib.algorithms_available), 'MARKDOWN_SPEECH')
		update.message.reply_markdown_v2(Caption, reply_to_message_id=update.message.message_id)

def cEval(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		update.message.reply_markdown_v2(
			CharEscape(choice(Locale.__('eval')), 'MARKDOWN_SPEECH'),
			reply_to_message_id=update.message.message_id)

def cExec(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Toks = GetRawTokens(update.message.text)
		if len(Toks) >= 2 and Toks[1].lower() in ('date', 'neofetch', 'uptime'):
			Caption = '```' + CharEscape(re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', subprocess.run(('sh', '-c', Toks[1].lower()), stdout=subprocess.PIPE).stdout.decode()) , 'MARKDOWN') + '```',
			update.message.reply_markdown_v2(
				# <https://stackoverflow.com/a/14693789>
				'```' + CharEscape( re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', subprocess.run(('sh', '-c', Toks[1].lower()), 
				stdout=subprocess.PIPE).stdout.decode()) , 'MARKDOWN') + '```',
				reply_to_message_id=update.message.message_id)
		else:
			update.message.reply_markdown_v2(
				CharEscape(choice(Locale.__('eval')), 'MARKDOWN_SPEECH'),
				reply_to_message_id=update.message.message_id)

#def CmdArgs(Msg:str, Cfg:tuple=None):
#	Args = []
#	Msg = Msg.strip().replace('\t', ' ')
#	if Cfg:
#		for i in Cfg:
#			Args += [Msg.replace('  ', ' ').replace('  ', ' ').split(' ')[:i]]
#			Msg = Msg
#	else:
#		return Msg.replace('  ', ' ').replace('  ', ' ').split(' ')

def CmdRestrict(update) -> bool:
	if not TGRestrict:
		return True
	else:
		if TGRestrict.lower() == 'whitelist':
			if update.message.chat.id in TGWhitelist:
				return True
	return False

#def SendMsg(Data, context):
#	pass

def Main() -> None:
	SetupDb()
	SetupLocale()

	#Private['Chats'].update({update.message.chat.id:{}})

	updater = Updater(TGToken)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('start', cStart))
	dispatcher.add_handler(CommandHandler('config', cConfig))
	dispatcher.add_handler(CommandHandler('help', cHelp))
	dispatcher.add_handler(CommandHandler('echo', cEcho))
	dispatcher.add_handler(CommandHandler('ping', cPing))
	dispatcher.add_handler(CommandHandler('time', cTime))
	dispatcher.add_handler(CommandHandler('hash', cHash))
	dispatcher.add_handler(CommandHandler('eval', cEval))
	dispatcher.add_handler(CommandHandler('exec', cExec))
	dispatcher.add_handler(CommandHandler('unsplash', cUnsplash))

	for Cmd in ('wish', 'level'):
		dispatcher.add_handler(CommandHandler(Cmd, percenter))
	for Cmd in ('hug', 'pat', 'poke', 'cuddle', 'floor', 'hands', 'sessocto'):
		dispatcher.add_handler(CommandHandler(Cmd, multifun))

	#dispatcher.add_handler(CommandHandler('setfilter', setfilter))
	dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, filters))

	print('Starting WinDog...')
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	Main()
	print('Closing WinDog...')
