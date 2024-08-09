# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cBroadcast(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if (data.user.id not in AdminIds) and (data.user.tag not in AdminIds):
		return send_status(context, 403, language)
	destination = data.command.arguments.destination
	text = (data.command.body or (data.quoted and data.quoted.text_plain))
	if not (destination and text):
		return send_status_400(context, language)
	result = send_message(context, {"text_plain": text, "room": SafeNamespace(id=destination)})
	send_message(context, {"text_plain": "Executed."})
	return result

RegisterModule(name="Broadcast", endpoints=[
	SafeNamespace(names=["broadcast"], handler=cBroadcast, body=True, arguments={
		"destination": True,
	}),
])

