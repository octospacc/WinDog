# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

def percenter(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	if len(Cmd.Tokens) >= 2:
		Text = choice(Locale.__(f'{Cmd.Name}.done'))
	else:
		Text = choice(Locale.__(f'{Cmd.Name}.empty'))
	update.message.reply_markdown_v2(
		CharEscape(Text, '.!<>').format(Cmd=Cmd.Tokens[0], Percent=RandPercent(), Thing=Cmd.Body),
		reply_to_message_id=update.message.message_id)

def multifun(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	Key = ParseCmd(update.message.text).Name
	ReplyToMsg = update.message.message_id
	if update.message.reply_to_message:
		ReplyFromUID = update.message.reply_to_message.from_user.id
		if ReplyFromUID == TGID and 'bot' in Locale.__(Key):
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

def cStart(Context, Data=None) -> None:
	SendMsg(Context, {"Text": "Hi stupid :3"})

#def cStart(update:Update, context:CallbackContext) -> None:
#	Cmd = HandleCmd(update)
#	if not Cmd: return
#	user = update.effective_user
#	update.message.reply_markdown_v2(#'Hi\!',
#		#CharEscape(choice(Locale.__('start')).format(CharEscape(user.mention_markdown_v2(), 'MARKDOWN')), 'MARKDOWN'),
#		CharEscape(choice(Locale.__('start')), '.!').format(user.mention_markdown_v2()),
#		reply_to_message_id=update.message.message_id)

def cHelp(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	update.message.reply_markdown_v2(
		CharEscape(choice(Locale.__('help')), 'MARKDOWN_SPEECH'),
		reply_to_message_id=update.message.message_id)

def cSource(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return

def cConfig(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	# ... area: eu, us, ...
	# ... language: en, it, ...
	# ... userdata: import, export, delete

def cEcho(Context, Data=None) -> None:
	if Data.Body:
		SendMsg(Context, {"Text": Data.Body})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('echo.empty'))})

def cEcho2(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	Msg = update.message.text
	if len(Msg.split(' ')) >= 2:
		Text = Msg[len(Msg.split(' ')[0])+1:]
		update.message.reply_text(
			Text,
			reply_to_message_id=update.message.message_id)
	else:
		Text = CharEscape(choice(Locale.__('echo.empty')), '.!')
		update.message.reply_markdown_v2(
			Text,
			reply_to_message_id=update.message.message_id)

def cPing(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	update.message.reply_markdown_v2(
		'*Pong\!*',
		reply_to_message_id=update.message.message_id)

#def cTime(update:Update, context:CallbackContext) -> None:
#	update.message.reply_markdown_v2(
#		CharEscape(choice(Locale.__('time')).format(time.ctime().replace('  ', ' ')), 'MARKDOWN_SPEECH'),
#		reply_to_message_id=update.message.message_id)

def cHash(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	if len(Cmd.Tokens) >= 3 and Cmd.Tokens[1] in hashlib.algorithms_available:
		Alg = Cmd.Tokens[1]
		Caption = hashlib.new(Alg, Alg.join(Cmd.Body.split(Alg)[1:]).strip().encode()).hexdigest()
	else:
		Caption = CharEscape(choice(Locale.__('hash')).format(Cmd.Tokens[0], hashlib.algorithms_available), 'MARKDOWN_SPEECH')
	update.message.reply_markdown_v2(Caption, reply_to_message_id=update.message.message_id)

def cEval(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	update.message.reply_markdown_v2(
		CharEscape(choice(Locale.__('eval')), 'MARKDOWN_SPEECH'),
		reply_to_message_id=update.message.message_id)

def cExec(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	Toks = Cmd.Tokens
	if len(Cmd.Tokens) >= 2 and Cmd.Tokens[1].lower() in ExecAllowed:
		Cmd = Toks[1].lower()
		Out = subprocess.run(('sh', '-c', f'export PATH=$PATH:/usr/games; {Cmd}'), stdout=subprocess.PIPE).stdout.decode()
		# <https://stackoverflow.com/a/14693789>
		Caption = (re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', Out)) #if ExecAllowed[Cmd] else Out)
		update.message.reply_markdown_v2(MarkdownCode(Caption, True), reply_to_message_id=update.message.message_id)
	else:
		update.message.reply_markdown_v2(
			CharEscape(choice(Locale.__('eval')), 'MARKDOWN_SPEECH'),
			reply_to_message_id=update.message.message_id)

def cWeb(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	Msg = update.message.text
	Toks = Cmd.Tokens
	if len(Cmd.Tokens) >= 2:
		try:
			Key = ParseCmd(Msg).Name
			Query = Key.join(Msg.split(Key)[1:]).strip()
			QueryUrl = UrlParse.quote(Query)
			Req = HttpGet(f'https://html.duckduckgo.com/html?q={QueryUrl}')
			Caption = f'[🦆🔎 "*{CharEscape(Query, "MARKDOWN")}*"](https://duckduckgo.com/?q={CharEscape(QueryUrl, "MARKDOWN")})\n\n'
			Index = 0
			for Line in Req.read().decode().replace('\t', ' ').splitlines():
				if ' class="result__a" ' in Line and ' href="//duckduckgo.com/l/?uddg=' in Line:
					Index += 1
					Link = CharEscape(UrlParse.unquote(Line.split(' href="//duckduckgo.com/l/?uddg=')[1].split('&amp;rut=')[0]), 'MARKDOWN')
					Title = CharEscape(UrlParse.unquote(Line.split('</a>')[0].split('</span>')[-1].split('>')[1]), 'MARKDOWN')
					Domain = Link.split('://')[1].split('/')[0]
					Caption += f'{Index}\. [{Title}]({Link}) \[`{Domain}`\]\n\n'
			update.message.reply_markdown_v2(Caption, reply_to_message_id=update.message.message_id)
		except Exception:
			raise

def cUnsplash(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	try:
		Req = HttpGet(f'https://source.unsplash.com/random/?{UrlParse.quote(Cmd.Body)}')
		update.message.reply_photo(
			Req.read(),
			caption=MarkdownCode(Req.geturl().split('?')[0], True),
			parse_mode='MarkdownV2',
			reply_to_message_id=update.message.message_id)
	except Exception:
		raise

def cSafebooru(update:Update, context:CallbackContext) -> None:
	Cmd = HandleCmd(update)
	if not Cmd: return
	ApiUrl = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100&tags='
	try:
		if Cmd.Body:
			for i in range(7):
				ImgUrls = HttpGet(f'{ApiUrl}md5:{RandHexStr(3)}%20{UrlParse.quote(Cmd.Body)}').read().decode().split(' file_url="')[1:]
				if ImgUrls:
					break
			if not ImgUrls:
				ImgUrls = HttpGet(f'{ApiUrl}{UrlParse.quote(Cmd.Body)}').read().decode().split(' file_url="')[1:]
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
			update.message.reply_photo(
				HttpGet(ImgUrl).read(),
				caption=f'`{ImgId}`\n' + MarkdownCode(ImgUrl, True),
				parse_mode='MarkdownV2',
				reply_to_message_id=update.message.message_id)
		else:
			pass
	except Exception:
		raise