# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cEcho(context:EventContext, data:InputMessageData):
	if not (text := data.command.body):
		return send_message(context, {
			"text_html": context.endpoint.get_string("empty", data.user.settings.language)})
	prefix = f'<a href="{data.message_url or ""}">🗣️</a> '
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
	return send_message(context, {"text_html": (prefix + html_escape(text))})

register_module(name="Echo", endpoints=[
	SafeNamespace(names=["echo"], handler=cEcho, body=True),
])

