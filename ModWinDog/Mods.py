# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from urlextract import URLExtract

# Module: Percenter
# Provides fun trough percentage-based toys.
def percenter(Context, Data=None) -> None:
	if Data.Body:
		Text = choice(Locale.__(f'{Data.Name}.done'))
	else:
		Text = choice(Locale.__(f'{Data.Name}.empty'))
	SendMsg(Context, {"Text": Text.format(Cmd=Data.Tokens[0], Percent=RandPercent(), Thing=Data.Body)})

# Module: Multifun
# Provides fun trough preprogrammed-text-based toys.
def multifun(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	Key = ParseCmd(update.message.text).Name
	ReplyToMsg = update.message.message_id
	if update.message.reply_to_message:
		ReplyFromUID = update.message.reply_to_message.from_user.id
		if ReplyFromUID == TelegramId and 'bot' in Locale.__(Key):
			Text = CharEscape(choice(Locale.__(f'{Key}.bot')), 'MARKDOWN_SPEECH')
		elif ReplyFromUID == update.message.from_user.id and 'self' in Locale.__(Key):
			FromUName = CharEscape(update.message.from_user.first_name, 'MARKDOWN')
			Text = CharEscape(choice(Locale.__(f'{Key}.self')), 'MARKDOWN_SPEECH').format(FromUName)
		else:
			if 'others' in Locale.__(Key):
				FromUName = CharEscape(update.message.from_user.first_name, 'MARKDOWN')
				ToUName = CharEscape(update.message.reply_to_message.from_user.first_name, 'MARKDOWN')
				Text = CharEscape(choice(Locale.__(f'{Key}.others')), 'MARKDOWN_SPEECH').format(FromUName,ToUName)
				ReplyToMsg = update.message.reply_to_message.message_id
	else:
		if 'empty' in Locale.__(Key):
			Text = CharEscape(choice(Locale.__(f'{Key}.empty')), 'MARKDOWN_SPEECH')
	update.message.reply_markdown_v2(Text, reply_to_message_id=ReplyToMsg)

# Module: Start
# Salutes the user, for now no other purpose except giving a feel that the bot is working.
def cStart(Context, Data=None) -> None:
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
	SendMsg(Context, {"TextPlain": "{https://gitlab.com/octospacc/WinDog}"})

# Module: Config
# ...
def cConfig(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	# ... area: eu, us, ...
	# ... language: en, it, ...
	# ... userdata: import, export, delete

# Module: Ping
# Responds pong, useful for testing messaging latency.
def cPing(Context, Data=None) -> None:
	SendMsg(Context, {"Text": "*Pong!*"})

# Module: Echo
# Responds back with the original text of the received message.
def cEcho(Context, Data=None) -> None:
	if Data.Body:
		SendMsg(Context, {"Text": Data.Body})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('echo.empty'))})

# Module: Broadcast
# Sends an admin message over to another destination
def cBroadcast(Context, Data=None) -> None:
	if len(Data.Tokens) >= 3 and Data.User['Id'] in AdminIds:
		Dest = Data.Tokens[1]
		Text = ' '.join(Data.Tokens[2:])
		SendMsg(Context, {"TextPlain": Text}, Dest)
		SendMsg(Context, {"TextPlain": "Executed."})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('eval'))})

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

# Module: Hash
# Responds with the hash-sum of a message received.
def cHash(Context, Data=None) -> None:
	if len(Data.Tokens) >= 3 and Data.Tokens[1] in hashlib.algorithms_available:
		Alg = Data.Tokens[1]
		Hash = hashlib.new(Alg, Alg.join(Data.Body.split(Alg)[1:]).strip().encode()).hexdigest()
		SendMsg(Context, {
			"TextPlain": Hash,
			"TextMarkdown": MarkdownCode(Hash, True),
		})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('hash.usage')).format(Data.Tokens[0], hashlib.algorithms_available)})

# Module: Eval
# Execute a Python command (or safe literal operation) in the current context. Currently not implemented.
def cEval(Context, Data=None) -> None:
	SendMsg(Context, {"Text": choice(Locale.__('eval'))})

# Module: Exec
# Execute a system command from the allowed ones and return stdout/stderr.
def cExec(Context, Data=None) -> None:
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

# Module: Embedded
# Rewrite a link trying to make sure we have an embed view.
def cEmbedded(Context, Data=None) -> None:
	if len(Data.Tokens) >= 2:
		# Find links in command body
		Text = Data.Body
	elif Data.Quoted and Data.Quoted['Body']:
		# Find links in quoted message
		Text = Data.Quoted['Body']
	else:
		# Error
		return
	pass
	Urls = URLExtract().find_urls(Text)
	if len(Urls) > 0:
		Proto = 'https://'
		Url = Urls[0]
		UrlLow = Url.lower()
		if UrlLow.startswith('http://') or UrlLow.startswith('https://'):
			Proto = Url.split('://')[0] + '://'
			Url = '://'.join(Url.split('://')[1:])
			UrlLow = '://'.join(UrlLow.split('://')[1:])
		if UrlLow.startswith('facebook.com/') or UrlLow.startswith('www.facebook.com/') or UrlLow.startswith('m.facebook.com/') or UrlLow.startswith('mbasic.facebook.com/'):
			Url = 'https://hlb0.octt.eu.org/cors-main.php/https://' + Url
			Proto = ''
		elif UrlLow.startswith('instagram.com/'):
			Url = 'ddinstagram.com/' + Url[len('instagram.com/'):]
		elif UrlLow.startswith('twitter.com/'):
			Url = 'fxtwitter.com/' + Url[len('twitter.com/'):]
		SendMsg(Context, {"TextPlain": Proto+Url})

# Module: Web
# Provides results of a DuckDuckGo search.
def cWeb(Context, Data=None) -> None:
	if Data.Body:
		try:
			QueryUrl = UrlParse.quote(Data.Body)
			Req = HttpGet(f'https://html.duckduckgo.com/html?q={QueryUrl}')
			Caption = f'🦆🔎 "{Data.Body}": https://duckduckgo.com/?q={QueryUrl}\n\n'
			Index = 0
			for Line in Req.read().decode().replace('\t', ' ').splitlines():
				if ' class="result__a" ' in Line and ' href="//duckduckgo.com/l/?uddg=' in Line:
					Index += 1
					Link = UrlParse.unquote(Line.split(' href="//duckduckgo.com/l/?uddg=')[1].split('&amp;rut=')[0])
					Title = HtmlUnescape(Line.split('</a>')[0].split('</span>')[-1].split('>')[1])
					Caption += f'[{Index}] {Title} : {{{Link}}}\n\n'
			SendMsg(Context, {"TextPlain": f'{Caption}...'})
		except Exception:
			raise
	else:
		pass

# Module: Translate
# Return the received message after translating it in another language.
def cTranslate(Context, Data=None) -> None:
	if Data.Body:
		try:
			Lang = Data.Tokens[1]
			# TODO: Use many different public Lingva instances in rotation to avoid overloading a specific one
			Result = json.loads(HttpGet(f'https://lingva.ml/api/v1/auto/{Lang}/{UrlParse.quote(Lang.join(Data.Body.split(Lang)[1:]))}').read())["translation"]
			SendMsg(Context, {"TextPlain": Result})
		except Exception:
			raise
	else:
		pass

# Module: Unsplash
# Send a picture sourced from Unsplash.
def cUnsplash(Context, Data=None) -> None:
	try:
		Req = HttpGet(f'https://source.unsplash.com/random/?{UrlParse.quote(Data.Body)}')
		ImgUrl = Req.geturl().split('?')[0]
		SendMsg(Context, {
			"TextPlain": f'{{{ImgUrl}}}',
			"TextMarkdown": MarkdownCode(ImgUrl, True),
			"Media": Req.read(),
		})
	except Exception:
		raise

# Module: Safebooru
# Send a picture sourced from Safebooru.
def cSafebooru(Context, Data=None) -> None:
	ApiUrl = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100&tags='
	try:
		if Data.Body:
			for i in range(7):
				ImgUrls = HttpGet(f'{ApiUrl}md5:{RandHexStr(3)}%20{UrlParse.quote(Data.Body)}').read().decode().split(' file_url="')[1:]
				if ImgUrls:
					break
			if not ImgUrls:
				ImgUrls = HttpGet(f'{ApiUrl}{UrlParse.quote(Data.Body)}').read().decode().split(' file_url="')[1:]
			ImgXml = choice(ImgUrls)
			ImgUrl = ImgXml.split('"')[0]
			ImgId = ImgXml.split(' id="')[1].split('"')[0]
		else:
			HtmlReq = HttpGet(HttpGet('https://safebooru.org/index.php?page=post&s=random').geturl())
			for Line in HtmlReq.read().decode().replace('\t', ' ').splitlines():
				if '<img ' in Line and ' id="image" ' in Line and ' src="':
					ImgUrl = Line.split(' src="')[1].split('"')[0]
					ImgId = ImgUrl.split('?')[-1]
					break
		if ImgUrl:
			SendMsg(Context, {
				"TextPlain": f'[{ImgId}]\n{{{ImgUrl}}}',
				"TextMarkdown": f'\\[`{ImgId}`\\]\n{MarkdownCode(ImgUrl, True)}',
				"Media": HttpGet(ImgUrl).read(),
			})
		else:
			pass
	except Exception:
		raise
