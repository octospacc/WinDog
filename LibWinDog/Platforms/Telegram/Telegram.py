# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start #

# TelegramToken = "1234567890:abcdefghijklmnopqrstuvwxyz123456789"

# TelegramGetterChannel = -1001234567890
# TelegramGetterGroup = -1001234567890

# end windog config # """

TelegramToken = None
TelegramGetterChannel = TelegramGetterGroup = None

import telegram, telegram.ext
#from telegram import Bot #, Update
#from telegram.helpers import escape_markdown
#from telegram.ext import Application, filters, CommandHandler, MessageHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from base64 import urlsafe_b64encode
from hashlib import sha256
from hmac import new as hmac_new

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
	if not user:
		return None
	return UserData(
		id = f"telegram:{user.id}",
		tag = user.username,
		name = user.first_name,
	)

def TelegramMakeInputMessageData(message:telegram.Message, access_token:str=None) -> InputMessageData:
	#if not message:
	#	return None
	timestamp = int(time.mktime(message.date.timetuple()))
	media = None
	if (photo := (message.photo and message.photo[-1])):
		media = {"url": photo.file_id, "type": "image/jpeg"}
	elif (video_note := message.video_note):
		media = {"url": video_note.file_id, "type": "video/mp4"}
	elif (media := (message.video or message.voice or message.audio or message.document or message.sticker)):
		media = {"url": media.file_id, "type": obj_get(media, "mime_type")}
	if (file_id := obj_get(media, "url")):
		media["url"] = f"telegram:{file_id}"
		if access_token:
			media["token"] = get_media_token_hash(media["url"], timestamp, access_token)
	data = InputMessageData(
		id = f"telegram:{message.message_id}",
		message_id = f"telegram:{message.message_id}",
		timestamp = timestamp,
		text_plain = (message.text or message.caption),
		text_markdown = message.text_markdown_v2,
		media = media,
		user = TelegramMakeUserData(message.from_user),
		room = SafeNamespace(
			id = f"telegram:{message.chat.id}",
			tag = message.chat.username,
			name = (message.chat.title or message.chat.first_name),
		),
	)
	data.command = TextCommandData(data.text_plain, "telegram")
	if data.user:
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

def TelegramGetter(context:EventContext, data:InputMessageData, access_token:str=None) -> InputMessageData:
	# bot API doesn't allow direct access of messages,
	# so we ask the server to copy it to a service channel, so that the API returns its data, then delete the copy
	message = TelegramMakeInputMessageData(
		context.manager.bot.forward_message(
			message_id=data.message_id,
			from_chat_id=data.room.id,
			chat_id=TelegramGetterChannel), access_token)
	delete_message(context, message)
	return message

def TelegramSender(context:EventContext, data:OutputMessageData):
	result = None
	# TODO clean this
	if data.room and (room_id := data.room.id):
		result = context.manager.bot.send_message(room_id, text=data.text_plain)
	else:
		replyToId = (data.ReplyTo or context.event.message.message_id)
		if data.media:
			for medium in data.media:
				result = obj_get(context.event.message, (
					"reply_photo" if medium.type.startswith("image/") else
					"reply_video" if medium.type.startswith("video/") else
				"reply_document"))(
					(medium.bytes or medium.url.removeprefix("telegram:")),
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

def TelegramDeleter(context:EventContext, data:MessageData):
	return context.manager.bot.delete_message(chat_id=data.room.id, message_id=data.message_id)

def TelegramFileGetter(context:EventContext, file_id:str, out=None):
	try:
		file = context.manager.bot.get_file(file_id)
		return (lambda: file.download(out=out)) if out else file.download_as_bytearray()
		#return file.download(out=out) if out else file.download_as_bytearray()
	except Exception:
		return None

# TODO support usernames
# TODO remove the platform stripping here (after modifying above functions here that use it), it's now implemented in get_link
def TelegramLinker(data:InputMessageData) -> SafeNamespace:
	linked = SafeNamespace()
	if (room_id := data.room.id):
		# prefix must be dropped for groups and channels, while direct chats apparently can never be linked
		if (room_id := "100".join(room_id.removeprefix("telegram:").split("100")[1:])):
			# apparently Telegram doesn't really support links to rooms by id without a message id, so we just use a null one
			linked.room = f"https://t.me/c/{room_id}/0"
			if data.message_id:
				message_id = data.message_id.removeprefix("telegram:")
				linked.message = f"https://t.me/c/{room_id}/{message_id}"
	return linked

register_platform(
	name="Telegram",
	main=TelegramMain,
	getter=TelegramGetter,
	linker=TelegramLinker,
	sender=TelegramSender,
	deleter=TelegramDeleter,
	filegetter=TelegramFileGetter,
	event_class=telegram.Update,
	manager_class=(lambda:TelegramClient),
	agent_info=(lambda:TelegramMakeUserData(TelegramClient.bot.get_me())),
)

