# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

# Module: Percenter
# Provides fun trough percentage-based toys.
def percenter(Context, Data) -> None:
	SendMsg(Context, {"Text": choice(Locale.__(f'{Data.Name}.{"done" if Data.Body else "empty"}')).format(
		Cmd=Data.Tokens[0], Percent=RandPercent(), Thing=Data.Body)})

# Module: Multifun
# Provides fun trough preprogrammed-text-based toys.
def multifun(Context, Data) -> None:
	cmdkey = Data.Name
	replyToId = None
	if Data.Quoted:
		replyFromUid = Data.Quoted.User["Id"]
		# TODO work on all platforms for the bot id
		if int(replyFromUid.split('@')[0]) == int(TelegramId) and 'bot' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.bot'))
		elif replyFromUid == Data.User["Id"] and 'self' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.self')).format(Data.User["Name"])
		else:
			if 'others' in Locale.__(cmdkey):
				Text = choice(Locale.__(f'{cmdkey}.others')).format(Data.User["Name"], Data.Quoted.User["Name"])
				replyToId = Data.Quoted.messageId
	else:
		if 'empty' in Locale.__(cmdkey):
			Text = choice(Locale.__(f'{cmdkey}.empty'))
	SendMsg(Context, {"Text": Text, "ReplyTo": replyToId})

# Module: Start
# Salutes the user, for now no other purpose except giving a feel that the bot is working.
def cStart(Context, Data) -> None:
	SendMsg(Context, {"Text": choice(Locale.__('start')).format(Data.User['Name'])})

# Module: Help
# Provides help for the bot. For now, it just lists the commands.
def cHelp(Context, Data=None) -> None:
	Commands = ''
	for Cmd in Endpoints.keys():
		Commands += f'* /{Cmd}\n'
	SendMsg(Context, {"TextPlain": f'Available Endpoints (WIP):\n{Commands}'})

# Module: Source
# Provides a copy of the bot source codes and/or instructions on how to get it.
def cSource(Context, Data=None) -> None:
	SendMsg(Context, {"TextPlain": ("""\
* Original Source Code: {https://gitlab.com/octospacc/WinDog}
  * Mirror: {https://github.com/octospacc/WinDog}
""" + (f"* Modified Source Code: {{{ModifiedSourceUrl}}}" if ModifiedSourceUrl else ""))})

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
def cPing(Context, Data=None) -> None:
	SendMsg(Context, {"Text": "*Pong!*"})

# Module: Echo
# Responds back with the original text of the received message.
def cEcho(Context, Data) -> None:
	if Data.Body:
		SendMsg(Context, {"Text": Data.Body})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('echo.empty'))})

# Module: Broadcast
# Sends an admin message over to another destination
def cBroadcast(Context, Data) -> None:
	if Data.User['Id'] not in AdminIds:
		return SendMsg(Context, {"Text": choice(Locale.__('eval'))})
	if len(Data.Tokens) < 3:
		return SendMsg(Context, {"Text": "Bad usage."})
	Dest = Data.Tokens[1]
	Text = ' '.join(Data.Tokens[2:])
	SendMsg(Context, {"TextPlain": Text}, Dest)
	SendMsg(Context, {"TextPlain": "Executed."})

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

# Module: Eval
# Execute a Python command (or safe literal operation) in the current context. Currently not implemented.
def cEval(Context, Data=None) -> None:
	SendMsg(Context, {"Text": choice(Locale.__('eval'))})

# Module: Exec
# Execute a system command from the allowed ones and return stdout/stderr.
def cExec(Context, Data) -> None:
	if len(Data.Tokens) >= 2 and Data.Tokens[1].lower() in ExecAllowed:
		Cmd = Data.Tokens[1].lower()
		Out = subprocess.run(('sh', '-c', f'export PATH=$PATH:/usr/games; {Cmd}'), stdout=subprocess.PIPE).stdout.decode()
		# <https://stackoverflow.com/a/14693789>
		Caption = (re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', Out))
		SendMsg(Context, {
			"TextPlain": Caption,
			"TextMarkdown": MarkdownCode(Caption, True),
		})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('eval'))})

# Module: Format
# Reformat text using an handful of rules. Currently not implemented.
def cFormat(Context, Data=None) -> None:
	pass

# Module: Frame
# Frame someone's message into a platform-styled image. Currently not implemented.
def cFrame(Context, Data=None) -> None:
	pass

