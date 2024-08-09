# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cSource(context:EventContext, data:InputMessageData):
	send_message(context, {"text_plain": ("""\
* Original Code: {https://gitlab.com/octospacc/WinDog}
  * Mirror: {https://github.com/octospacc/WinDog}
""" + (f"* Modified Code: {{{ModifiedSourceUrl}}}" if ModifiedSourceUrl else ""))})

def cGdpr(context:EventContext, data:InputMessageData):
	pass

UserSettingsLimits = {
	"language": 13,
}

def cConfig(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not (settings := UserSettingsData(data.user.id)):
		User.update(settings=EntitySettings.create()).where(User.id == data.user.id).execute()
		settings = UserSettingsData(data.user.id)
	if not (key := data.command.arguments.get) or (key not in UserSettingsLimits):
		return send_status_400(context, language)
	if (value := data.command.body):
		if len(value) > UserSettingsLimits[key]:
			return send_status(context, 500, language)
		EntitySettings.update(**{key: value}).where(EntitySettings.entity == data.user.id).execute()
		settings = UserSettingsData(data.user.id)
	if (key):
		# TODO show a hint on possible options? and add proper text hints for results
		return send_message(context, {"text_plain": str(obj_get(settings, key))})
	# TODO show general help when no useful parameters are passed
	# ... area: eu, us, ...
	# ... language: en, it, ...
	# ... userdata: import, export, delete

def cPing(context:EventContext, data:InputMessageData):
	# nice experiment, but it won't work with Telegram since time is not to milliseconds (?)
	#time_diff = (time_now := int(time.time())) - (time_sent := data.datetime)
	#send_message(context, OutputMessageData(text_html=f"<b>Pong!</b>\n\n{time_sent} → {time_now} = {time_diff}"))
	send_message(context, OutputMessageData(text_html="<b>Pong!</b>"))

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

#def cEval(context:EventContext, data:InputMessageData) -> None:
#	send_message(context, {"Text": choice(Locale.__('eval'))})

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

