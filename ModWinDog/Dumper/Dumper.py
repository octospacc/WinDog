# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from json import dumps as json_dumps

# TODO: assume current room when none specified
def get_message_wrapper(context:EventContext, data:InputMessageData):
	if check_bot_admin(data.user) and (message_id := data.command.arguments.message_id) and (room_id := (data.command.arguments.room_id or data.room.id)):
		return get_message(context, {"message_id": message_id, "room": {"id": room_id}})

# TODO dump and getmessage should work with links to messages!

# TODO can we somehow read the quoted message's quoted message on Telegram?
def cDump(context:EventContext, data:InputMessageData):
	if not (message := (data.quoted or get_message_wrapper(context, data))):
		return send_status_400(context, data.user.settings.language)
	text = data_to_json(message, indent="  ")
	return send_message(context, {"text_html": f'<pre>{html_escape(text)}</pre>'})

def cGetLink(context:EventContext, data:InputMessageData):
	if not (message := (data.quoted or get_message_wrapper(context, data))):
		return send_status_400(context, data.user.settings.language)
	text = ''
	if (url := message.message_url):
		text += f"Message: {url}\n"
	if (media := message.media) and (url := media.url):
		link = get_media_link(url, type=media.type, timestamp=message.timestamp, access_token=tuple(WebTokens)[0])
		text += f"Media: {link or url}\n"
	if not text:
		return send_status_400(context, data.user.settings.language)
	return send_message(context, {"text_plain": text})

def cGetMessage(context:EventContext, data:InputMessageData):
	if not (message := get_message_wrapper(context, data)):
		return send_status_400(context, data.user.settings.language)
	return send_message(context, ObjectUnion(message, {"room": None}))

register_module(name="Dumper", group="Geek", endpoints=[
	SafeNamespace(names=["dump"], handler=cDump, quoted=True, arguments={
		"message_id": True,
		"room_id": True,
	}),
	SafeNamespace(names=["getlink"], handler=cGetLink, quoted=True, arguments={
		"message_id": True,
		"room_id": True,
	}),
	SafeNamespace(names=["getmessage"], handler=cGetMessage, arguments={
		"message_id": True,
		"room_id": True,
	}),
])

