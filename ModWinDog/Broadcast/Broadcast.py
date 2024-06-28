# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

def cBroadcast(context:EventContext, data:InputMessageData) -> None:
	if (data.user.id not in AdminIds) and (data.user.tag not in AdminIds):
		return SendMessage(context, {"Text": choice(Locale.__('eval'))})
	destination = data.command.arguments["destination"]
	if not (destination and data.command.body):
		return SendMessage(context, {"Text": "Bad usage."})
	SendMessage(context, {"TextPlain": data.command.body}, destination)
	SendMessage(context, {"TextPlain": "Executed."})

RegisterModule(name="Broadcast", endpoints=[
	SafeNamespace(names=["broadcast"], handler=cBroadcast, arguments={
		"destination": True,
	}),
])

