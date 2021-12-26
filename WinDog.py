#!/usr/bin/env python3

import json
from random import choice, randint
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from Config import *

Private = {}
Locale = {}

def MDSanitize(String, Exclude=[]):
	for c in ['!', '.']:
		if c not in Exclude:
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
		update.message.reply_text(
			choice(Locale[Lang]['help']),
			reply_to_message_id=update.message.message_id)

def echo(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		Message = update.message.text
		if Message.lower()[1:] == 'echo':
			Text = choice(Locale[Lang]['echo']['empty'])
		else:
			Text = Message[5:]
		update.message.reply_text(
			Text,
			reply_to_message_id=update.message.message_id)

def ping(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		update.message.reply_text(
			'Pong!',
			reply_to_message_id=update.message.message_id)

def wish(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		if update.message.text.lower()[1:] == 'wish':
			Text = choice(Locale[Lang]['wish']['empty'])
		else:
			Text = choice(Locale[Lang]['wish']['done'])
		update.message.reply_markdown_v2(
			MDSanitize(Text).format(randint(0,100)),
			reply_to_message_id=update.message.message_id)

def hug(update:Update, context:CallbackContext) -> None:
	if CmdRestrict(update):
		if update.message.reply_to_message:
			FromUser = update.message.from_user.first_name.replace('.','\.')
			ToUser = update.message.reply_to_message.from_user.first_name.replace('.','\.')
			Text = MDSanitize(choice(Locale[Lang]['hug']['others'])).format(FromUser,ToUser)
		else:
			Text = MDSanitize(choice(Locale[Lang]['hug']['empty']))
		update.message.reply_markdown_v2(
			Text,
			reply_to_message_id=update.message.message_id)

def filters(update:Update, context:CallbackContext, Private) -> None:
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

def setfilter(update:Update, context:CallbackContext, Private) -> None:
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
	dispatcher.add_handler(CommandHandler("hug", hug))
	#dispatcher.add_handler(CommandHandler("pat", pat))
	#dispatcher.add_handler(CommandHandler("poke", poke))
	#dispatcher.add_handler(CommandHandler("cuddle", cuddle))
	#dispatcher.add_handler(CommandHandler("setfilter", setfilter))
	dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, filters, Private))

	print('Starting bot...')
	updater.start_polling()

	updater.idle()

if __name__ == '__main__':
	main()
	print('Closing...')
