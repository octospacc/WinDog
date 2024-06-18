# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start #

# TelegramToken = "1234567890:abcdefghijklmnopqrstuvwxyz123456789"

# end windog config # """

TelegramToken = None

import telegram, telegram.ext
from telegram import ForceReply, Bot #, Update
#from telegram.helpers import escape_markdown
#from telegram.ext import Application, filters, CommandHandler, MessageHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

def TelegramMain() -> bool:
	if not TelegramToken:
		return False
	updater = telegram.ext.Updater(TelegramToken)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(MessageHandler(Filters.text | Filters.command, TelegramHandlerWrapper))
	updater.start_polling()
	#app = Application.builder().token(TelegramToken).build()
	#app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, TelegramHandler))
	#app.run_polling(allowed_updates=Update.ALL_TYPES)
	return True

def TelegramHandlerWrapper(update:telegram.Update, context:CallbackContext=None) -> None:
	Thread(target=lambda:TelegramHandlerCore(update, context)).start()

def TelegramHandlerCore(update:telegram.Update, context:CallbackContext=None) -> None:
	if not update.message:
		return
	data = SimpleNamespace()
	data.room_id = f"{update.message.chat.id}@telegram"
	data.message_id = f"{update.message.message_id}@telegram"
	data.text_plain = update.message.text
	data.text_markdown = update.message.text_markdown_v2
	data.text_auto = GetWeightedText(data.text_markdown, data.text_plain)
	data.command = ParseCommand(data.text_plain)
	data.user = SimpleNamespace()
	data.user.name = update.message.from_user.first_name
	data.user.tag = update.message.from_user.username
	data.user.id = f"{update.message.from_user.id}@telegram"
	OnMessageParsed(data)
	cmd = ParseCmd(update.message.text)
	if cmd:
		cmd.command = data.command
		cmd.messageId = update.message.message_id
		cmd.TextPlain = cmd.Body
		cmd.TextMarkdown = update.message.text_markdown_v2
		cmd.Text = GetWeightedText(cmd.TextMarkdown, cmd.TextPlain)
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
					"Text": GetWeightedText(update.message.reply_to_message.text_markdown_v2, update.message.reply_to_message.text),
					"User": SimpleNamespace(**{
						"Name": update.message.reply_to_message.from_user.first_name,
						"Tag": update.message.reply_to_message.from_user.username,
						"Id": f'{update.message.reply_to_message.from_user.id}@telegram',
					}),
				})
			Endpoints[cmd.Name]["handler"]({"Event": update, "Manager": context}, cmd)

def TelegramSender(event, manager, data, destination, textPlain, textMarkdown) -> None:
	if destination:
		manager.bot.send_message(destination, text=textPlain)
	else:
		replyToId = (data["ReplyTo"] if ("ReplyTo" in data and data["ReplyTo"]) else event.message.message_id)
		if InDict(data, "Media") and not InDict(data, "media"):
			data["media"] = {"bytes": data["Media"]}
		if InDict(data, "media"):
			#data["media"] = SureArray(data["media"])
			#media = (data["media"][0]["bytes"] if "bytes" in data["media"][0] else data["media"][0]["url"])
			#if len(data["media"]) > 1:
			#	media_list = []
			#	media_list.append(telegram.InputMediaPhoto(
			#		media[0],
			#		caption=(textMarkdown if textMarkdown else textPlain if textPlain else None),
			#		parse_mode=("MarkdownV2" if textMarkdown else None)))
			#	for medium in media[1:]:
			#		media_list.append(telegram.InputMediaPhoto(medium))
			#	event.message.reply_media_group(media_list, reply_to_message_id=replyToId)
			#else:
			#	event.message.reply_photo(
			#		media,
			#		caption=(textMarkdown if textMarkdown else textPlain if textPlain else None),
			#		parse_mode=("MarkdownV2" if textMarkdown else None),
			#		reply_to_message_id=replyToId)
			#event.message.reply_photo(
			#	(DictGet(media[0], "bytes") or DictGet(media[0], "url")),
			#	caption=(textMarkdown if textMarkdown else textPlain if textPlain else None),
			#	parse_mode=("MarkdownV2" if textMarkdown else None),
			#	reply_to_message_id=replyToId)
			#for medium in media[1:]:
			#	event.message.reply_photo((DictGet(medium, "bytes") or DictGet(medium, "url")), reply_to_message_id=replyToId)
			for medium in SureArray(data["media"]):
				event.message.reply_photo(
					(DictGet(medium, "bytes") or DictGet(medium, "url")),
					caption=(textMarkdown if textMarkdown else textPlain if textPlain else None),
					parse_mode=("MarkdownV2" if textMarkdown else None),
					reply_to_message_id=replyToId)
		elif textMarkdown:
			event.message.reply_markdown_v2(textMarkdown, reply_to_message_id=replyToId)
		elif textPlain:
			event.message.reply_text(textPlain, reply_to_message_id=replyToId)

RegisterPlatform(name="Telegram", main=TelegramMain, sender=TelegramSender, eventClass=telegram.Update)

