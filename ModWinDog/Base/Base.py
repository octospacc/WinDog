# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import re, subprocess

def cStart(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"Text": choice(Locale.__('start')).format(data.User.Name)})

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
	if (get := ObjGet(data, "command.arguments.get")):
		SendMessage(context, OutputMessageData(text_plain=str(ObjGet(data.user.settings, get))))
	#Cmd = TelegramHandleCmd(update)
	#if not Cmd: return
	# ... area: eu, us, ...
	# ... language: en, it, ...
	# ... userdata: import, export, delete

def cPing(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"Text": "*Pong!*"})

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

def cEval(context:EventContext, data:InputMessageData) -> None:
	SendMessage(context, {"Text": choice(Locale.__('eval'))})

def cExec(context:EventContext, data:InputMessageData) -> None:
	if len(data.Tokens) >= 2 and data.Tokens[1].lower() in ExecAllowed:
		cmd = data.Tokens[1].lower()
		Out = subprocess.run(('sh', '-c', f'export PATH=$PATH:/usr/games; {cmd}'),
			stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
		# <https://stackoverflow.com/a/14693789>
		Caption = (re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', Out))
		SendMessage(context, {
			"TextPlain": Caption,
			"TextMarkdown": MarkdownCode(Caption, True),
		})
	else:
		SendMessage(context, {"Text": choice(Locale.__('eval'))})

RegisterModule(name="Misc", endpoints=[
	SafeNamespace(names=["start"], summary="Salutes the user, hinting that the bot is working and providing basic quick help.", handler=cStart),
	SafeNamespace(names=["source"], summary="Provides a copy of the bot source codes and/or instructions on how to get it.", handler=cSource),
	SafeNamespace(names=["config"], handler=cConfig, arguments={
		"get": True,
	}),
	#SafeNamespace(names=["gdpr"], summary="Operations for european citizens regarding your personal data.", handler=cGdpr),
	SafeNamespace(names=["ping"], summary="Responds pong, useful for testing messaging latency.", handler=cPing),
	SafeNamespace(names=["eval"], summary="Execute a Python command (or safe literal operation) in the current context. Currently not implemented.", handler=cEval),
	SafeNamespace(names=["exec"], summary="Execute a system command from the allowed ones and return stdout+stderr.", handler=cExec),
	#SafeNamespace(names=["format"], summary="Reformat text using an handful of rules. Not yet implemented.", handler=cFormat),
	#SafeNamespace(names=["frame"], summary="Frame someone's message into a platform-styled image. Not yet implemented.", handler=cFrame),
	#SafeNamespace(names=["repeat"], summary="I had this planned but I don't remember what this should have done. Not yet implemented.", handler=cRepeat),
])

