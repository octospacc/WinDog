# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

# TODO: implement /help <commandname> feature
def cHelp(context, data=None) -> None:
	moduleList = ''
	for module in Modules:
		summary = Modules[module]["summary"]
		endpoints = Modules[module]["endpoints"]
		moduleList += (f"\n\n{module}" + (f": {summary}" if summary else ''))
		for endpoint in endpoints:
			summary = endpoints[endpoint]["summary"]
			moduleList += (f"\n* /{', /'.join(endpoints[endpoint]['names'])}" + (f": {summary}" if summary else ''))
	SendMsg(context, {"Text": f"[ Available Modules ]{moduleList}"})

RegisterModule(name="Help", group="Basic", endpoints={
	"Help": CreateEndpoint(["help"], summary="Provides help for the bot. For now, it just lists the commands.", handler=cHelp),
})

