# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

def mMultifun(context:EventContext, data:InputMessageData) -> None:
	cmdkey = data.command.name
	replyToId = None
	if data.quoted:
		replyFromUid = data.quoted.user.id
		# TODO work on all platforms for the bot id
		if replyFromUid.split(':')[1] == TelegramToken.split(':')[0] and 'bot' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.bot'))
		elif replyFromUid == data.user.id and 'self' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.self')).format(data.user.name)
		else:
			if 'others' in Locale.__(cmdkey):
				Text = choice(Locale.__(f'{cmdkey}.others')).format(data.user.name, data.quoted.user.name)
				replyToId = data.quoted.message_id
	else:
		if 'empty' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.empty'))
	SendMessage(context, {"Text": Text, "ReplyTo": replyToId})

RegisterModule(name="Multifun", endpoints=[
	SafeNamespace(names=["hug", "pat", "poke", "cuddle", "hands", "floor", "sessocto"], handler=mMultifun),
])

