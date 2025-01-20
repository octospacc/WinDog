# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cBroadcast(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not check_bot_admin(data.user):
		return send_status(context, 403, language)
	destination = data.command.arguments.destination
	text = (data.command.body or (data.quoted and data.quoted.text_plain))
	if not (destination and text):
		return send_status_400(context, language)
	result = send_message(context, {"text_plain": text, "room": SafeNamespace(id=destination)})
	send_status(context, 201, language)
	return result

register_module(name="Broadcast", endpoints=[
	SafeNamespace(names=["broadcast"], handler=cBroadcast, body=True, arguments={
		"destination": True,
	}),
])

