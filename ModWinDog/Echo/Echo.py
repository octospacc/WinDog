# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cEcho(context:EventContext, data:InputMessageData) -> None:
	if not (text := ObjGet(data, "command.body")):
		return SendMessage(context, {
			"text_html": context.endpoint.get_string("empty", data.user.settings.language)})
	prefix = f'<a href="{data.message_url}">🗣️</a> '
	if len(data.command.tokens) == 2: # text is a single word
		nonascii = True
		for char in data.command.tokens[1]:
			if ord(char) < 256:
				nonascii = False
				break
		if nonascii:
			# word is not ascii, probably an emoji (altough not necessarily)
			# so just pass it as is (useful for Telegram emojis)
			prefix = ''
	SendMessage(context, {"text_html": (prefix + html_escape(text))})

RegisterModule(name="Echo", endpoints=[
	SafeNamespace(names=["echo"], handler=cEcho, body=True),
])

