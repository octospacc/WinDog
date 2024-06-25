# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

from json import dumps as json_dumps

def cDump(context:EventContext, data:InputMessageData):
	if not (message := ObjGet(data, "quoted")):
		pass
	SendMessage(context, {"TextPlain": json_dumps(message, default=(lambda obj: obj.__dict__), indent="  ")})

RegisterModule(name="Dumper", group="Geek", endpoints=[
	SafeNamespace(names=["dump"], handler=cDump),
])

