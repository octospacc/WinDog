# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def mMultifun(context:EventContext, data:InputMessageData) -> None:
	cmdkey = data.Name
	replyToId = None
	if data.Quoted:
		replyFromUid = data.Quoted.User.Id
		# TODO work on all platforms for the bot id
		if replyFromUid.split(':')[1] == TelegramToken.split(':')[0] and 'bot' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.bot'))
		elif replyFromUid == data.User.Id and 'self' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.self')).format(data.User.Name)
		else:
			if 'others' in Locale.__(cmdkey):
				Text = choice(Locale.__(f'{cmdkey}.others')).format(data.User.Name, data.Quoted.User.Name)
				replyToId = data.Quoted.messageId
	else:
		if 'empty' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.empty'))
	SendMessage(context, {"Text": Text, "ReplyTo": replyToId})

RegisterModule(name="Multifun", endpoints=[
	SafeNamespace(names=["hug", "pat", "poke", "cuddle", "hands", "floor", "sessocto"], summary="Provides fun trough preprogrammed-text-based toys.", handler=mMultifun),
])

