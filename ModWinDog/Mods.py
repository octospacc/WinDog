# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

# Module: Percenter
# Provides fun trough percentage-based toys.
def percenter(context, data) -> None:
	SendMsg(context, {"Text": choice(Locale.__(f'{data.Name}.{"done" if data.Body else "empty"}')).format(
		Cmd=data.Tokens[0], Percent=RandPercent(), Thing=data.Body)})

# Module: Multifun
# Provides fun trough preprogrammed-text-based toys.
def multifun(context, data) -> None:
	cmdkey = data.Name
	replyToId = None
	if data.Quoted:
		replyFromUid = data.Quoted.User.Id
		# TODO work on all platforms for the bot id
		if int(replyFromUid.split('@')[0]) == int(TelegramId) and 'bot' in Locale.__(cmdkey):
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

# Module: Start
# Salutes the user, hinting that the bot is working and providing basic quick help.
def cStart(context, data) -> None:
	SendMsg(context, {"Text": choice(Locale.__('start')).format(data.User.Name)})

# Module: Source
# Provides a copy of the bot source codes and/or instructions on how to get it.
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

# Module: Ping
# Responds pong, useful for testing messaging latency.
def cPing(context, data=None) -> None:
	SendMsg(context, {"Text": "*Pong!*"})

# Module: Echo
# Responds back with the original text of the received message.
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

# Module: Broadcast
# Sends an admin message over to another destination
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

# Module: Eval
# Execute a Python command (or safe literal operation) in the current context. Currently not implemented.
def cEval(context, data=None) -> None:
	SendMsg(context, {"Text": choice(Locale.__('eval'))})

# Module: Exec
# Execute a system command from the allowed ones and return stdout/stderr.
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

# Module: Format
# Reformat text using an handful of rules. Currently not implemented.
def cFormat(context, data=None) -> None:
	pass

# Module: Frame
# Frame someone's message into a platform-styled image. Currently not implemented.
def cFrame(context, data=None) -> None:
	pass

