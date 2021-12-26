#!/usr/bin/env python3

# =================================== #
# WinDog multi-purpose chatbot
# Licensed under AGPLv3 by OctoSpacc
# =================================== #

import json
from random import choice, randint
from telegram import Update, ForceReply, Bot
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from Config import *

Private = {}
Locale = {}

def CharEscape(String, Escape=''):
	if Escape == 'MARKDOWN':
		return escape_markdown(String, version=2)
	elif Escape == 'MARKDOWN_SPEECH':
		for c in '.!()[]':
			String = String.replace(c, '\\'+c)
		return String
	else:
		for c in Escape:
			String = String.replace(c, '\\'+c)
		return String

def start(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		user = update.effective_user
		update.message.reply_markdown_v2(
			fr'Hi {user.mention_markdown_v2()}\!',
			#reply_markup=ForceReply(selective=True),
		)

def help(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		update.message.reply_markdown_v2(
			CharEscape(choice(Locale[Lang]['help']), '.!()'),
			reply_to_message_id=update.message.message_id)

def echo(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Message = update.message.text
		if Message.lower()[1:] == 'echo':
			Text = CharEscape(choice(Locale[Lang]['echo']['empty']), '.!')
		else:
			Text = Message[5:]
		update.message.reply_markdown_v2(
			Text,
			reply_to_message_id=update.message.message_id)

def ping(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		update.message.reply_markdown_v2(
			'*Pong\!*',
			reply_to_message_id=update.message.message_id)

def wish(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		if update.message.text.lower()[1:] == 'wish':
			Text = choice(Locale[Lang]['wish']['empty'])
		else:
			Text = choice(Locale[Lang]['wish']['done'])
		update.message.reply_markdown_v2(
			CharEscape(Text, '.!').format(str(randint(0,100))+'\.'+str(randint(0,9))+str(randint(0,9))),
			reply_to_message_id=update.message.message_id)

def multifun(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Key = update.message.text.split(' ')[0][1:]
		ReplyToMessage = update.message.message_id
		if update.message.reply_to_message:
			ReplyFromUID = update.message.reply_to_message.from_user.id
			if ReplyFromUID == TGID:
				Text = CharEscape(choice(Locale[Lang][Key]['bot']), 'MARKDOWN_SPEECH')
			elif ReplyFromUID == update.message.from_user.id:
				FromUName = CharEscape(update.message.from_user.first_name, 'MARKDOWN')
				Text = CharEscape(choice(Locale[Lang][Key]['self']), 'MARKDOWN_SPEECH').format(FromUName)
			else:
				FromUName = CharEscape(update.message.from_user.first_name, 'MARKDOWN')
				ToUName = CharEscape(update.message.reply_to_message.from_user.first_name, 'MARKDOWN')
				Text = CharEscape(choice(Locale[Lang][Key]['others']), 'MARKDOWN_SPEECH').format(FromUName,ToUName)
				ReplyToMessage = update.message.reply_to_message.message_id
		else:
			Text = CharEscape(choice(Locale[Lang][Key]['empty']), 'MARKDOWN_SPEECH')
		update.message.reply_markdown_v2(
			Text,
			reply_to_message_id=ReplyToMessage)


def filters(update:Update, context:CallbackContext) -> None:
	pass
	"""
	if CmdRestrict(update):
		ChatID = update.message.chat.id
		if ChatID in Private['Chats'] and 'Filters' in Private['Chats'][ChatID]:
			for f in Private['Chats'][ChatID]['Filters']:
				if f in update.message.text:
					update.message.reply_text(
						Private['Chats'][ChatID]['Filters'][f],
						reply_to_message_id=update.message.message_id)
	"""

def setfilter(update:Update, context:CallbackContext) -> None:
	pass
	"""
	if CmdRestrict(update):
		ChatID = update.message.chat.id
		if ChatID not in Private['Chats'] or 'Filters' not in Private['Chats'][ChatID]:
			Private['Chats'][ChatID] = {'Filters':{}}
		Private['Chats'][ChatID]['Filters'][update.message.text] = {'Text':0}
	"""

def CmdRestrict(update):
	if not TGRestrict:
		return True
	else:
		if TGRestrict == 'Whitelist':
			if update.message.chat.id in TGWhitelist:
				return True
	return False

def main() -> None:
	global Private, Locale

	try:
		with open('Private.json', 'r') as File:
			Private = json.load(File)
	except Exception:
		Private = {}
	if 'Chats' not in Private:
		Private['Chats'] = {}

	try:
		with open('Locale/{0}.json'.format(Lang)) as File:
			Locale[Lang] = json.load(File)
	except Exception:
		print('Cannot load {0} locale, exiting'.format(Lang))
		raise
		exit(1)

	#Private['Chats'].update({update.message.chat.id:{}})

	updater = Updater(TGToken)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("help", help))
	dispatcher.add_handler(CommandHandler("echo", echo))
	dispatcher.add_handler(CommandHandler("ping", ping))
	dispatcher.add_handler(CommandHandler("wish", wish))
	dispatcher.add_handler(CommandHandler("hug", multifun))
	dispatcher.add_handler(CommandHandler("pat", multifun))
	dispatcher.add_handler(CommandHandler("poke", multifun))
	dispatcher.add_handler(CommandHandler("cuddle", multifun))
	#dispatcher.add_handler(CommandHandler("setfilter", setfilter))
	dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, filters))

	print('Starting WinDog...')
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
	print('Closing WinDog...')
