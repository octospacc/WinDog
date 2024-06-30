# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cEcho(context:EventContext, data:InputMessageData) -> None:
	if not (text := ObjGet(data, "command.body")):
		return SendMessage(context, {"text_html": context.endpoint.get_string("empty", data.user.settings.language)})
	prefix = f'<a href="{data.message_url}">🗣️</a> '
	#prefix = f"[🗣️]({context.linker(data).message}) "
	if len(data.command.tokens) == 2:
		nonascii = True
		for char in data.command.tokens[1]:
			if ord(char) < 256:
				nonascii = False
				break
		if nonascii:
			# text is not ascii, probably an emoji (altough not necessarily), so just pass as is (useful for Telegram emojis)
			prefix = ''
	SendMessage(context, {"text_html": (prefix + html_escape(text))})

RegisterModule(name="Echo", endpoints=[
	SafeNamespace(names=["echo"], handler=cEcho),
])

