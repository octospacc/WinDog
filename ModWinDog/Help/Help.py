# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

# TODO: implement /help <commandname> feature
def cHelp(context:EventContext, data:InputMessageData) -> None:
	module_list = ''
	language = data.user.settings.language
	for module in Modules:
		summary = Modules[module].get_string("summary", language)
		endpoints = Modules[module].endpoints
		module_list += (f"\n\n{module}" + (f": {summary}" if summary else ''))
		for endpoint in endpoints:
			summary = Modules[module].get_string(f"endpoints.{endpoint.names[0]}.summary", language)
			module_list += (f"\n* /{', /'.join(endpoint.names)}" + (f": {summary}" if summary else ''))
	SendMessage(context, OutputMessageData(text=module_list))

RegisterModule(name="Help", group="Basic", endpoints=[
	SafeNamespace(names=["help"], handler=cHelp),
])

