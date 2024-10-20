# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start #

# TelegramToken = "1234567890:abcdefghijklmnopqrstuvwxyz123456789"

# end windog config # """

TelegramToken = None

import telegram, telegram.ext
from telegram import Bot #, Update
#from telegram.helpers import escape_markdown
#from telegram.ext import Application, filters, CommandHandler, MessageHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

TelegramClient = None

def TelegramMain(path:str) -> bool:
	if not TelegramToken:
		return False
	global TelegramClient
	TelegramClient = telegram.ext.Updater(TelegramToken)
	TelegramClient.dispatcher.add_handler(MessageHandler(Filters.text | Filters.command, TelegramHandler))
	TelegramClient.start_polling()
	#app = Application.builder().token(TelegramToken).build()
	#app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, TelegramHandler))
	#app.run_polling(allowed_updates=Update.ALL_TYPES)
	return True

def TelegramMakeUserData(user:telegram.User) -> UserData:
	return UserData(
		id = f"telegram:{user.id}",
		tag = user.username,
		name = user.first_name,
	)

def TelegramMakeInputMessageData(message:telegram.Message) -> InputMessageData:
	#if not message:
	#	return None
	data = InputMessageData(
		message_id = f"telegram:{message.message_id}",
		datetime = int(time.mktime(message.date.timetuple())),
		text_plain = message.text,
		text_markdown = message.text_markdown_v2,
		user = TelegramMakeUserData(message.from_user),
		room = SafeNamespace(
			id = f"telegram:{message.chat.id}",
			tag = message.chat.username,
			name = (message.chat.title or message.chat.first_name),
		),
	)
	data.command = TextCommandData(data.text_plain, "telegram")
	data.user.settings = UserSettingsData(data.user.id)
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
		on_input_message_parsed(data)
		call_endpoint(EventContext(platform="telegram", event=update, manager=context), data)
	Thread(target=handler).start()

def TelegramSender(context:EventContext, data:OutputMessageData):
	result = None
	# TODO clean this
	if data.room and (room_id := data.room.id):
		result = context.manager.bot.send_message(room_id, text=data.text_plain)
	else:
		replyToId = (data.ReplyTo or context.event.message.message_id)
		if data.media:
			for medium in data.media:
				result = context.event.message.reply_photo(
					(obj_get(medium, "bytes") or obj_get(medium, "url")),
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
	if (room_id := data.room.id):
		# prefix must be dropped for groups and channels, while direct chats apparently can never be linked
		if (room_id := "100".join(room_id.split("telegram:")[1].split("100")[1:])):
			# apparently Telegram doesn't really support links to rooms by id without a message id, so we just use a null one
			linked.room = f"https://t.me/c/{room_id}/0"
			if data.message_id:
				message_id = data.message_id.split("telegram:")[1]
				linked.message = f"https://t.me/c/{room_id}/{message_id}"
	return linked

register_platform(
	name="Telegram",
	main=TelegramMain,
	sender=TelegramSender,
	linker=TelegramLinker,
	event_class=telegram.Update,
	manager_class=(lambda:TelegramClient),
	agent_info=(lambda:TelegramMakeUserData(TelegramClient.bot.get_me())),
)

