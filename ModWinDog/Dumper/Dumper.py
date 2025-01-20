# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from json import dumps as json_dumps, loads as json_loads

def dict_filter_meta(dikt:dict):
	remove = []
	for key in dikt:
		if key.startswith('_'):
			remove.append(key)
		elif type(obj := dikt[key]) == dict:
			dikt[key] = dict_filter_meta(obj)
	for key in remove:
		dikt.pop(key)
	return dikt

# TODO: assume current room when none specified
def get_message_wrapper(context:EventContext, data:InputMessageData):
	if check_bot_admin(data.user) and (message_id := data.command.arguments.message_id) and (room_id := (data.command.arguments.room_id or data.room.id)):
		return get_message(context, {"message_id": message_id, "room": {"id": room_id}})

# TODO work with links to messages
def cDump(context:EventContext, data:InputMessageData):
	if not (message := (data.quoted or get_message_wrapper(context, data))):
		return send_status_400(context, data.user.settings.language)
	data = dict_filter_meta(json_loads(json_dumps(message, default=(lambda obj: (obj.__dict__ if not callable(obj) else None)))))
	text = json_dumps(data, indent="  ")
	return send_message(context, {"text_html": f'<pre>{html_escape(text)}</pre>'})

def cGetMessage(context:EventContext, data:InputMessageData):
	if not (message := get_message_wrapper(context, data)):
		return send_status_400(context, data.user.settings.language)
	return send_message(context, ObjectUnion(message, {"room": None}))

register_module(name="Dumper", group="Geek", endpoints=[
	SafeNamespace(names=["dump"], handler=cDump, quoted=True, arguments={
		"message_id": True,
		"room_id": True,
	}),
	SafeNamespace(names=["getmessage"], handler=cGetMessage, arguments={
		"message_id": True,
		"room_id": True,
	}),
])

