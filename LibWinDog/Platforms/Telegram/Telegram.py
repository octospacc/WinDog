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
	dispatcher.add_handler(MessageHandler(Filters.text | Filters.command, TelegramHandler))
	updater.start_polling()
	#app = Application.builder().token(TelegramToken).build()
	#app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, TelegramHandler))
	#app.run_polling(allowed_updates=Update.ALL_TYPES)
	return True

def TelegramMakeInputMessageData(message:telegram.Message) -> InputMessageData:
	#if not message:
	#	return None
	data = InputMessageData(
		message_id = f"telegram:{message.message_id}",
		datetime = int(time.mktime(message.date.timetuple())),
		text_plain = message.text,
		text_markdown = message.text_markdown_v2,
		user = SafeNamespace(
			id = f"telegram:{message.from_user.id}",
			tag = message.from_user.username,
			name = message.from_user.first_name,
		),
		room = SafeNamespace(
			id = f"telegram:{message.chat.id}",
			tag = message.chat.username,
			name = (message.chat.title or message.chat.first_name),
		),
	)
	data.text_auto = GetWeightedText(data.text_markdown, data.text_plain)
	data.command = ParseCommand(data.text_plain)
	data.user.settings = (GetUserSettings(data.user.id) or SafeNamespace())
	linked = TelegramLinker(data)
	data.message_url = linked.message
	data.room.url = linked.room
	return data

def TelegramHandler(update:telegram.Update, context:CallbackContext=None) -> None:
	def handler() -> None:
		if not update.message:
			return
		data = TelegramMakeInputMessageData(update.message)
		if (quoted := update.message.reply_to_message):
			data.quoted = TelegramMakeInputMessageData(quoted)
		OnMessageParsed(data)
		if (command := ObjGet(data, "command.name")):
			CallEndpoint(command, EventContext(platform="telegram", event=update, manager=context), data)
	Thread(target=handler).start()

def TelegramSender(context:EventContext, data:OutputMessageData, destination):
	result = None
	if destination:
		result = context.manager.bot.send_message(destination, text=data.text_plain)
	else:
		replyToId = (data.ReplyTo or context.event.message.message_id)
		if data.media:
			for medium in data.media:
				result = context.event.message.reply_photo(
					(ObjGet(medium, "bytes") or ObjGet(medium, "url")),
					caption=(data.text_html or data.text_markdown or data.text_plain),
					parse_mode=("HTML" if data.text_html else "MarkdownV2" if data.text_markdown else None),
					reply_to_message_id=replyToId)
		elif data.text_html:
			result = context.event.message.reply_html(data.text_html, reply_to_message_id=replyToId)
		elif data.text_markdown:
			result = context.event.message.reply_markdown_v2(data.text_markdown, reply_to_message_id=replyToId)
		elif data.text_plain:
			result = context.event.message.reply_text(data.text_plain, reply_to_message_id=replyToId)
	return TelegramMakeInputMessageData(result)

# TODO support usernames
def TelegramLinker(data:InputMessageData) -> SafeNamespace:
	linked = SafeNamespace()
	if data.room.id:
		# prefix must be dropped for groups and channels, while direct chats apparently can never be linked
		if (room_id := "100".join(data.room.id.split("telegram:")[1].split("100")[1:])):
			# apparently Telegram doesn't really support links to rooms by id without a message id, so we just use a null one
			linked.room = f"https://t.me/c/{room_id}/0"
			if data.message_id:
				message_id = data.message_id.split("telegram:")[1]
				linked.message = f"https://t.me/c/{room_id}/{message_id}"
	return linked

RegisterPlatform(name="Telegram", main=TelegramMain, sender=TelegramSender, linker=TelegramLinker, eventClass=telegram.Update)

