# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

def cSource(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"TextPlain": ("""\
* Original Code: {https://gitlab.com/octospacc/WinDog}
  * Mirror: {https://github.com/octospacc/WinDog}
""" + (f"* Modified Code: {{{ModifiedSourceUrl}}}" if ModifiedSourceUrl else ""))})

def cGdpr(context:EventContext, data:InputMessageData) -> None:
	pass

def cConfig(context:EventContext, data:InputMessageData) -> None:
	if not (settings := GetUserSettings(data.user.id)):
		User.update(settings=EntitySettings.create()).where(User.id == data.user.id).execute()
	if (to_set := ObjGet(data, "command.arguments.set")):
		pass # TODO set in db, but first we need to ensure data is handled safely
	if (to_get := ObjGet(data, "command.arguments.get")):
		# TODO show a hint on possible options?
		return SendMessage(context, OutputMessageData(text_plain=str(ObjGet(data.user.settings, to_get))))
	# TODO show general help when no useful parameters are passed
	#Cmd = TelegramHandleCmd(update)
	#if not Cmd: return
	# ... area: eu, us, ...
	# ... language: en, it, ...
	# ... userdata: import, export, delete

def cPing(context:EventContext, data:InputMessageData) -> None:
	# nice experiment, but it won't work with Telegram since time is not to milliseconds (?)
	#time_diff = (time_now := int(time.time())) - (time_sent := data.datetime)
	#SendMessage(context, OutputMessageData(text_html=f"<b>Pong!</b>\n\n{time_sent} → {time_now} = {time_diff}"))
	SendMessage(context, OutputMessageData(text_html="<b>Pong!</b>"))

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

#def cEval(context:EventContext, data:InputMessageData) -> None:
#	SendMessage(context, {"Text": choice(Locale.__('eval'))})

RegisterModule(name="Base", endpoints=[
	SafeNamespace(names=["source"], handler=cSource),
	SafeNamespace(names=["config"], handler=cConfig, body=False, arguments={
		"get": True,
	}),
	#SafeNamespace(names=["gdpr"], summary="Operations for european citizens regarding your personal data.", handler=cGdpr),
	SafeNamespace(names=["ping"], handler=cPing),
	#SafeNamespace(names=["eval"], summary="Execute a Python command (or safe literal operation) in the current context. Currently not implemented.", handler=cEval),
	#SafeNamespace(names=["format"], summary="Reformat text using an handful of rules. Not yet implemented.", handler=cFormat),
	#SafeNamespace(names=["frame"], summary="Frame someone's message into a platform-styled image. Not yet implemented.", handler=cFrame),
	#SafeNamespace(names=["repeat"], summary="I had this planned but I don't remember what this should have done. Not yet implemented.", handler=cRepeat),
])

