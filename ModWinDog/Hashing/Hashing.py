# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import hashlib

def cHash(context:EventContext, data:InputMessageData):
	text_input = (data.command.body or (data.quoted and data.quoted.text_plain))
	algorithm = data.command.arguments.algorithm
	language = data.user.settings.language
	if not (text_input and (algorithm in hashlib.algorithms_available)):
		return SendMessage(context, {
			"text_html": f'{context.endpoint.help_text(language)}\n\n{context.endpoint.get_string("algorithms", language)}: {hashlib.algorithms_available}'})
	hashed = hashlib.new(algorithm, text_input.encode()).hexdigest()
	return SendMessage(context, {"text_html": f"<pre>{hashed}</pre>"})

RegisterModule(name="Hashing", group="Geek", endpoints=[
	SafeNamespace(names=["hash"], handler=cHash, body=False, quoted=False, arguments={
		"algorithm": True,
	}),
])

