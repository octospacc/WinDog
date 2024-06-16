# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

TelegramToken = None

import telegram, telegram.ext
from telegram import ForceReply, Bot
from telegram.utils.helpers import escape_markdown
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

def TelegramMain() -> bool:
	if not TelegramToken:
		return False
	updater = telegram.ext.Updater(TelegramToken)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(MessageHandler(Filters.text | Filters.command, TelegramHandler))
	updater.start_polling()
	return True

def TelegramHandler(update:telegram.Update, context:CallbackContext=None) -> None:
	if not (update and update.message):
		return
	OnMessageReceived()
	cmd = ParseCmd(update.message.text)
	if cmd:
		cmd.messageId = update.message.message_id
		cmd.TextPlain = cmd.Body
		cmd.TextMarkdown = update.message.text_markdown_v2
		cmd.Text = GetWeightedText((cmd.TextMarkdown, cmd.TextPlain))
		if cmd.Tokens[0][0] in CmdPrefixes and cmd.Name in Endpoints:
			cmd.User = SimpleNamespace(**{
				"Name": update.message.from_user.first_name,
				"Tag": update.message.from_user.username,
				"Id": f'{update.message.from_user.id}@telegram',
			})
			if update.message.reply_to_message:
				cmd.Quoted = SimpleNamespace(**{
					"messageId": update.message.reply_to_message.message_id,
					"Body": update.message.reply_to_message.text,
					"TextPlain": update.message.reply_to_message.text,
					"TextMarkdown": update.message.reply_to_message.text_markdown_v2,
					"Text": GetWeightedText((update.message.reply_to_message.text_markdown_v2, update.message.reply_to_message.text)),
					"User": SimpleNamespace(**{
						"Name": update.message.reply_to_message.from_user.first_name,
						"Tag": update.message.reply_to_message.from_user.username,
						"Id": f'{update.message.reply_to_message.from_user.id}@telegram',
					}),
				})
			Endpoints[cmd.Name]({"Event": update, "Manager": context}, cmd)
	if Debug and Dumper:
		Text = update.message.text
		Text = (Text.replace('\n', '\\n') if Text else '')
		with open('Dump.txt', 'a') as File:
			File.write(f'[{time.ctime()}] [{int(time.time())}] [{update.message.chat.id}] [{update.message.message_id}] [{update.message.from_user.id}] {Text}\n')

def TelegramSender(event, manager, Data, Destination, TextPlain, TextMarkdown) -> None:
	if Destination:
		manager.bot.send_message(Destination, text=TextPlain)
	else:
		replyToId = (Data["ReplyTo"] if ("ReplyTo" in Data and Data["ReplyTo"]) else event.message.message_id)
		if InDict(Data, 'Media'):
			event.message.reply_photo(
				Data['Media'],
				caption=(TextMarkdown if TextMarkdown else TextPlain if TextPlain else None),
				parse_mode=('MarkdownV2' if TextMarkdown else None),
				reply_to_message_id=replyToId,
			)
		elif TextMarkdown:
			event.message.reply_markdown_v2(TextMarkdown, reply_to_message_id=replyToId)
		elif TextPlain:
			event.message.reply_text(TextPlain, reply_to_message_id=replyToId)

RegisterPlatform(name="Telegram", main=TelegramMain, sender=TelegramSender, eventClass=telegram.Update)

