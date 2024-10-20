# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

# NOTE: with this implementation there is a 1/100 probability (high!) of result 100.00, which is not always ideal
def RandomPercentString() -> str:
	num = randint(0,100)
	return (f'{num}.00' if num == 100 else f'{num}.{randint(0,9)}{randint(0,9)}')

def mPercenter(context:EventContext, data:InputMessageData):
	return send_message(context, {"text_html": (context.endpoint.get_string(
			("done" if data.command.body else "empty"),
			data.user.settings.language
		) or context.endpoint.get_help_text(data.user.settings.language)
	).format(RandomPercentString(), data.command.body)})

register_module(name="Percenter", endpoints=[
	SafeNamespace(names=["wish", "level"], handler=mPercenter, body=True),
])

