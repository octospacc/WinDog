# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cEcho(context:EventContext, data:InputMessageData) -> None:
	text = ObjGet(data, "command.body")
	if text:
		prefix = "🗣️ "
		#prefix = f"[🗣️]({context.linker(data).message}) "
		if len(data.Tokens) == 2:
			nonascii = True
			for char in data.Tokens[1]:
				if ord(char) < 256:
					nonascii = False
					break
			if nonascii:
				# text is not ascii, probably an emoji (altough not necessarily), so just pass as is (useful for Telegram emojis)
				prefix = ''
		SendMessage(context, OutputMessageData(text=(prefix + text)))
	else:
		SendMessage(context, OutputMessageData(text_html=context.endpoint.get_string('empty')))

RegisterModule(name="Echo", endpoints=[
	SafeNamespace(names=["echo"], handler=cEcho),
])

