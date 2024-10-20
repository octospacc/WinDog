# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import hashlib

def cHash(context:EventContext, data:InputMessageData):
	text_input = (data.command.body or (data.quoted and data.quoted.text_plain))
	algorithm = data.command.arguments.algorithm
	if not (text_input and (algorithm in hashlib.algorithms_available)):
		return send_status_400(context, data.user.settings.language)
	return send_message(context, {
		"text_html": f"<pre>{html_escape(hashlib.new(algorithm, text_input.encode()).hexdigest())}</pre>"})

register_module(name="Hashing", group="Geek", endpoints=[
	SafeNamespace(names=["hash"], handler=cHash, body=False, quoted=False, arguments={
		"algorithm": True,
	}, help_extra=(lambda endpoint, lang: f'{endpoint.get_string("algorithms", lang)}: <code>{"</code>, <code>".join(hashlib.algorithms_available)}</code>.')),
])

