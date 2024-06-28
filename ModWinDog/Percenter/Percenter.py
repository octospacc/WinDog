# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def mPercenter(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"Text": choice(Locale.__(f'{data.command.name}.{"done" if data.command.body else "empty"}')).format(
		Cmd=data.command.tokens[0], Percent=RandPercent(), Thing=data.command.body)})

RegisterModule(name="Percenter", endpoints=[
	SafeNamespace(names=["wish", "level"], handler=mPercenter),
])

