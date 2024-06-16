# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import re, subprocess

def mPercenter(context, data) -> None:
	SendMsg(context, {"Text": choice(Locale.__(f'{data.Name}.{"done" if data.Body else "empty"}')).format(
		Cmd=data.Tokens[0], Percent=RandPercent(), Thing=data.Body)})

def mMultifun(context, data) -> None:
	cmdkey = data.Name
	replyToId = None
	if data.Quoted:
		replyFromUid = data.Quoted.User.Id
		# TODO work on all platforms for the bot id
		if replyFromUid.split('@')[0] == TelegramToken.split(':')[0] and 'bot' in Locale.__(cmdkey):
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
	SendMsg(context, {"Text": Text, "ReplyTo": replyToId})

def cStart(context, data) -> None:
	SendMsg(context, {"Text": choice(Locale.__('start')).format(data.User.Name)})

def cSource(context, data=None) -> None:
	SendMsg(context, {"TextPlain": ("""\
* Original Code: {https://gitlab.com/octospacc/WinDog}
  * Mirror: {https://github.com/octospacc/WinDog}
""" + (f"* Modified Code: {{{ModifiedSourceUrl}}}" if ModifiedSourceUrl else ""))})

# Module: Config
# ...
#def cConfig(update:telegram.Update, context:CallbackContext) -> None:
#	Cmd = TelegramHandleCmd(update)
#	if not Cmd: return
#	# ... area: eu, us, ...
#	# ... language: en, it, ...
#	# ... userdata: import, export, delete

def cPing(context, data=None) -> None:
	SendMsg(context, {"Text": "*Pong!*"})

def cEcho(context, data) -> None:
	if data.Body:
		prefix = "🗣️ "
		if len(data.Tokens) == 2:
			nonascii = True
			for char in data.Tokens[1]:
				if ord(char) < 256:
					nonascii = False
					break
			if nonascii:
				# text is not ascii, probably an emoji (altough not necessarily), so just pass as is (useful for Telegram emojis)
				prefix = ''
		SendMsg(context, {"Text": (prefix + data.Body)})
	else:
		SendMsg(context, {"Text": choice(Locale.__('echo.empty'))})

def cBroadcast(context, data) -> None:
	if data.User.Id not in AdminIds:
		return SendMsg(context, {"Text": choice(Locale.__('eval'))})
	if len(data.Tokens) < 3:
		return SendMsg(context, {"Text": "Bad usage."})
	Dest = data.Tokens[1]
	Text = ' '.join(data.Tokens[2:])
	SendMsg(context, {"TextPlain": Text}, Dest)
	SendMsg(context, {"TextPlain": "Executed."})

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

def cEval(context, data=None) -> None:
	SendMsg(context, {"Text": choice(Locale.__('eval'))})

def cExec(context, data) -> None:
	if len(data.Tokens) >= 2 and data.Tokens[1].lower() in ExecAllowed:
		cmd = data.Tokens[1].lower()
		Out = subprocess.run(('sh', '-c', f'export PATH=$PATH:/usr/games; {cmd}'),
			stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
		# <https://stackoverflow.com/a/14693789>
		Caption = (re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', Out))
		SendMsg(context, {
			"TextPlain": Caption,
			"TextMarkdown": MarkdownCode(Caption, True),
		})
	else:
		SendMsg(context, {"Text": choice(Locale.__('eval'))})

RegisterModule(name="Misc", endpoints={
	"Percenter": CreateEndpoint(["wish", "level"], summary="Provides fun trough percentage-based toys.", handler=mPercenter),
	"Multifun": CreateEndpoint(["hug", "pat", "poke", "cuddle", "hands", "floor", "sessocto"], summary="Provides fun trough preprogrammed-text-based toys.", handler=mMultifun),
	"Start": CreateEndpoint(["start"], summary="Salutes the user, hinting that the bot is working and providing basic quick help.", handler=cStart),
	"Source": CreateEndpoint(["source"], summary="Provides a copy of the bot source codes and/or instructions on how to get it.", handler=cSource),
	"Ping": CreateEndpoint(["ping"], summary="Responds pong, useful for testing messaging latency.", handler=cPing),
	"Echo": CreateEndpoint(["echo"], summary="Responds back with the original text of the received message.", handler=cEcho),
	"Broadcast": CreateEndpoint(["broadcast"], summary="Sends an admin message over to any chat destination.", handler=cBroadcast),
	"Eval": CreateEndpoint(["eval"], summary="Execute a Python command (or safe literal operation) in the current context. Currently not implemented.", handler=cEval),
	"Exec": CreateEndpoint(["exec"], summary="Execute a system command from the allowed ones and return stdout+stderr.", handler=cExec),
	#"Format": CreateEndpoint(["format"], summary="Reformat text using an handful of rules. Not yet implemented.", handler=cFormat),
	#"Frame": CreateEndpoint(["frame"], summary="Frame someone's message into a platform-styled image. Not yet implemented.", handler=cFrame),
	#"Repeat": CreateEndpoint(["repeat"], summary="I had this planned but I don't remember what this should have done. Not yet implemented.", handler=cRepeat),
})

