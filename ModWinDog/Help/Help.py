# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

# TODO: implement /help <commandname> feature
def cHelp(context:EventContext, data:InputMessageData) -> None:
	text = (context.endpoint.get_string(lang=data.user.settings.language) or '').strip()
	language = data.user.settings.language
	for module in Modules:
		summary = Modules[module].get_string("summary", language)
		endpoints = Modules[module].endpoints
		text += (f"\n\n{module}" + (f": {summary}" if summary else ''))
		for endpoint in endpoints:
			summary = Modules[module].get_string(f"endpoints.{endpoint.names[0]}.summary", language)
			text += (f"\n* /{', /'.join(endpoint.names)}" + (f": {summary}" if summary else ''))
		text = text.strip()
	SendMessage(context, {"text_html": text})

RegisterModule(name="Help", group="Basic", endpoints=[
	SafeNamespace(names=["help"], handler=cHelp),
])

