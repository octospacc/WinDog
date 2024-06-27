# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cStart(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, OutputMessageData(
		text_html=context.endpoint.get_string(
			"start", data.user.settings.language).format(data.user.name)))

RegisterModule(name="Start", endpoints=[
	SafeNamespace(names=["start"], handler=cStart),
])

