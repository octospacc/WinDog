# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cHelp(context:EventContext, data:InputMessageData) -> None:
	language = data.user.settings.language
	prefix = data.command.prefix
	if (endpoint := data.command.arguments.endpoint):
		if endpoint[0] in CommandPrefixes:
			endpoint = endpoint[1:]
		if endpoint in Endpoints:
			return send_message(context, {"text_html": get_help_text(endpoint, language, prefix)})
	text = (context.endpoint.get_string(lang=data.user.settings.language) or '').strip()
	for group in ModuleGroups:
		text += f"\n\n[ {group} ]"
		for module in ModuleGroups[group]:
			summary = Modules[module].get_string("summary", language)
			endpoints = Modules[module].endpoints
			text += (f"\n\n{module}" + (f": {summary}" if summary else ''))
			for endpoint in endpoints:
				summary = Modules[module].get_string(f"endpoints.{endpoint.names[0]}.summary", language)
				text += (f"\n* {prefix}{f', {prefix}'.join(endpoint.names)}"
					+ (f": {summary}" if summary else ''))
			text = text.strip()
	return send_message(context, {"text_html": text})

RegisterModule(name="Help", group="Basic", endpoints=[
	SafeNamespace(names=["help"], handler=cHelp, arguments={
		"endpoint": False,
	}),
])

