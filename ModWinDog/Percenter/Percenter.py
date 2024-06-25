# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def mPercenter(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"Text": choice(Locale.__(f'{data.Name}.{"done" if data.Body else "empty"}')).format(
		Cmd=data.Tokens[0], Percent=RandPercent(), Thing=data.Body)})

RegisterModule(name="Percenter", endpoints=[
	SafeNamespace(names=["wish", "level"], summary="Provides fun trough percentage-based toys.", handler=mPercenter),
])

