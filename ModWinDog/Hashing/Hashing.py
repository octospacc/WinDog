# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import hashlib

def cHash(context:EventContext, data:InputMessageData):
	text_input = ObjGet(data, "command.body")
	algorithm = ObjGet(data, "command.arguments.algorithm")
	if not (text_input and (algorithm in hashlib.algorithms_available)):
		return SendMessage(context, {"Text": choice(Locale.__('hash.usage')).format(data.command.tokens[0], hashlib.algorithms_available)})
	hashed = hashlib.new(algorithm, text_input.encode()).hexdigest()
	return SendMessage(context, OutputMessageData(text_plain=hashed, text_html=f"<pre>{hashed}</pre>"))

RegisterModule(name="Hashing", group="Geek", endpoints=[
	SafeNamespace(names=["hash"], handler=cHash, arguments={
		"algorithm": True,
	}),
])

