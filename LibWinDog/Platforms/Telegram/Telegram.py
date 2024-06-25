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

def TelegramMakeInputMessageData(message:telegram.Message) -> InputMessageData:
	data = InputMessageData(
		message_id = f"telegram:{message.message_id}",
		text_plain = message.text,
		text_markdown = message.text_markdown_v2,
	)
	data.text_auto = GetWeightedText(data.text_markdown, data.text_plain)
	data.command = ParseCommand(data.text_plain)
	data.room = SafeNamespace(
		id = f"telegram:{message.chat.id}",
		tag = message.chat.username,
		name = (message.chat.title or message.chat.first_name),
	)
	data.user = SafeNamespace(
		id = f"telegram:{message.from_user.id}",
		tag = message.from_user.username,
		name = message.from_user.first_name,
	)
	#if (db_user := GetUserData(data.user.id)):
	#	data.user.language = db_user.language
	return data

def TelegramHandlerWrapper(update:telegram.Update, context:CallbackContext=None) -> None:
	Thread(target=lambda:TelegramHandlerCore(update, context)).start()

def TelegramHandlerCore(update:telegram.Update, context:CallbackContext=None) -> None:
	if not update.message:
		return
	data = TelegramMakeInputMessageData(update.message)
	if update.message.reply_to_message:
		data.quoted = TelegramMakeInputMessageData(update.message.reply_to_message)
	OnMessageParsed(data)
	cmd = ParseCmd(update.message.text)
	if cmd:
		cmd.command = data.command
		cmd.quoted = data.quoted
		cmd.messageId = update.message.message_id
		cmd.TextPlain = cmd.Body
		cmd.TextMarkdown = update.message.text_markdown_v2
		cmd.Text = GetWeightedText(cmd.TextMarkdown, cmd.TextPlain)
		if cmd.Tokens[0][0] in CmdPrefixes and cmd.Name in Endpoints:
			cmd.User = SimpleNamespace(**{
				"Name": update.message.from_user.first_name,
				"Tag": update.message.from_user.username,
				"Id": f'telegram:{update.message.from_user.id}',
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
						"Id": f'telegram:{update.message.reply_to_message.from_user.id}',
					}),
				})
			CallEndpoint(cmd.Name, EventContext(platform="telegram", event=update, manager=context), cmd)

def TelegramSender(context:EventContext, data:OutputMessageData, destination, textPlain, textMarkdown):
	result = None
	if destination:
		result = context.manager.bot.send_message(destination, text=textPlain)
	else:
		replyToId = (data["ReplyTo"] if ("ReplyTo" in data and data["ReplyTo"]) else context.event.message.message_id)
		if InDict(data, "Media") and not InDict(data, "media"):
			data["media"] = {"bytes": data["Media"]}
		if InDict(data, "media"):
			for medium in SureArray(data["media"]):
				result = context.event.message.reply_photo(
					(DictGet(medium, "bytes") or DictGet(medium, "url")),
					caption=(textMarkdown if textMarkdown else textPlain if textPlain else None),
					parse_mode=("MarkdownV2" if textMarkdown else None),
					reply_to_message_id=replyToId)
		elif textMarkdown:
			result = context.event.message.reply_markdown_v2(textMarkdown, reply_to_message_id=replyToId)
		elif textPlain:
			result = context.event.message.reply_text(textPlain, reply_to_message_id=replyToId)
	return TelegramMakeInputMessageData(result)

def TelegramLinker(data:InputMessageData) -> SafeNamespace:
	linked = SafeNamespace()
	if data.room.id:
		room_id = data.room.id.split("telegram:")[1]
		linked.room = f"https://t.me/{room_id}"
	if data.message_id:
		message_id = data.message_id.split("telegram:")[1]
		linked.message = f"{linked.room}/{message_id}"
	return linked

RegisterPlatform(name="Telegram", main=TelegramMain, sender=TelegramSender, linker=TelegramLinker, eventClass=telegram.Update)

