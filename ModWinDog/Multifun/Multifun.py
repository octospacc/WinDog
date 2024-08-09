# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def mMultifun(context:EventContext, data:InputMessageData):
	reply_to = None
	fun_strings = {}
	for key in ("empty", "bot", "self", "others"):
		fun_strings[key] = context.endpoint.get_string(key, data.user.settings.language)
	if data.quoted:
		if fun_strings["bot"] and (data.quoted.user.id == Platforms[context.platform].agent_info.id):
			text = choice(fun_strings["bot"])
		elif fun_strings["self"] and (data.quoted.user.id == data.user.id):
			text = choice(fun_strings["self"]).format(data.user.name)
		elif fun_strings["others"]:
			text = choice(fun_strings["others"]).format(data.user.name, data.quoted.user.name)
			reply_to = data.quoted.message_id
	else:
		if fun_strings["empty"]:
			text = choice(fun_strings["empty"])
	return send_message(context, {"text_html": text, "ReplyTo": reply_to})

RegisterModule(name="Multifun", endpoints=[
	SafeNamespace(names=["hug", "pat", "poke", "cuddle", "hands", "floor", "sessocto"], handler=mMultifun),
])

