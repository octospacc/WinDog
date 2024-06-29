# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

def cBroadcast(context:EventContext, data:InputMessageData) -> None:
	if (data.user.id not in AdminIds) and (data.user.tag not in AdminIds):
		return SendMessage(context, {"Text": choice(Locale.__('eval'))})
	destination = data.command.arguments["destination"]
	text = data.command.body
	if not (destination and text):
		return SendMessage(context, OutputMessageData(text_plain="Bad usage."))
	SendMessage(context, OutputMessageData(text_plain=text, room_id=destination))
	SendMessage(context, OutputMessageData(text_plain="Executed."))

RegisterModule(name="Broadcast", endpoints=[
	SafeNamespace(names=["broadcast"], handler=cBroadcast, arguments={
		"destination": True,
	}),
])

