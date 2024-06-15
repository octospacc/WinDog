from urlextract import URLExtract
from urllib import parse as UrlParse
from urllib.request import urlopen, Request

def HttpGet(Url:str):
	return urlopen(Request(Url, headers={"User-Agent": WebUserAgent}))

# Module: Embedded
# Rewrite a link trying to make sure we have an embed view.
def cEmbedded(Context, Data) -> None:
	if len(Data.Tokens) >= 2:
		# Find links in command body
		Text = (Data.TextMarkdown + ' ' + Data.TextPlain)
	elif Data.Quoted and Data.Quoted.Text:
		# Find links in quoted message
		Text = (Data.Quoted.TextMarkdown + ' ' + Data.Quoted.TextPlain)
	else:
		# TODO Error message
		return
	pass
	urls = URLExtract().find_urls(Text)
	if len(urls) > 0:
		proto = 'https://'
		url = urls[0]
		urlLow = url.lower()
		if urlLow.startswith('http://') or urlLow.startswith('https://'):
			proto = url.split('://')[0] + '://'
			url = '://'.join(url.split('://')[1:])
			urlLow = '://'.join(urlLow.split('://')[1:])
		urlDomain = urlLow.split('/')[0]
		if urlDomain in ("facebook.com", "www.facebook.com", "m.facebook.com", "mbasic.facebook.com"):
			url = "https://hlb0.octt.eu.org/cors-main.php/https://" + url
			proto = ''
		else:
			if urlDomain == "instagram.com":
				urlDomain = "ddinstagram.com"
			elif urlDomain in ("twitter.com", "x.com"):
				urlDomain = "fxtwitter.com"
			elif urlDomain == "vm.tiktok.com":
				urlDomain = "vm.vxtiktok.com"
			url = urlDomain + url[len(urlDomain):]
		SendMsg(Context, {"TextPlain": f"{{{proto}{url}}}"})
	# else TODO error message?

# Module: Web
# Provides results of a DuckDuckGo search.
def cWeb(Context, Data) -> None:
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
					Title = Line.strip().split('</a>')[0].strip().split('</span>')[-1].strip().split('>')
					if len(Title) > 1:
						Title = HtmlUnescape(Title[1].strip())
						Caption += f'[{Index}] {Title} : {{{Link}}}\n\n'
					else:
						continue
			SendMsg(Context, {"TextPlain": f'{Caption}...'})
		except Exception:
			raise
	else:
		pass

# Module: Translate
# Return the received message after translating it in another language.
def cTranslate(Context, Data) -> None:
	if len(Data.Tokens) < 3:
		return
	try:
		Lang = Data.Tokens[1]
		# TODO: Use many different public Lingva instances in rotation to avoid overloading a specific one
		Result = json.loads(HttpGet(f'https://lingva.ml/api/v1/auto/{Lang}/{UrlParse.quote(Lang.join(Data.Body.split(Lang)[1:]))}').read())["translation"]
		SendMsg(Context, {"TextPlain": Result})
	except Exception:
		raise

# Module: Unsplash
# Send a picture sourced from Unsplash.
def cUnsplash(Context, Data) -> None:
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
def cSafebooru(Context, Data) -> None:
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

