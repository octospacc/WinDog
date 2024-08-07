# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def mPercenter(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"text_html": (context.endpoint.get_string(
			("done" if data.command.body else "empty"),
			data.user.settings.language
		) or context.endpoint.help_text(data.user.settings.language)
	).format(RandPercent(), data.command.body)})

RegisterModule(name="Percenter", endpoints=[
	SafeNamespace(names=["wish", "level"], handler=mPercenter, body=True),
])

