# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start # """

MicrosoftBingSettings = {}

""" # end windog config # """

from urlextract import URLExtract
from urllib import parse as UrlParse
from urllib.request import urlopen, Request

def HttpReq(url:str, method:str|None=None, *, body:bytes=None, headers:dict[str, str]={"User-Agent": WebUserAgent}):
	return urlopen(Request(url, method=method, data=body, headers=headers))

def cEmbedded(context:EventContext, data:InputMessageData) -> None:
	if len(data.Tokens) >= 2:
		# Find links in command body
		Text = (data.TextMarkdown + ' ' + data.TextPlain)
	elif data.Quoted and data.Quoted.Text:
		# Find links in quoted message
		Text = (data.Quoted.TextMarkdown + ' ' + data.Quoted.TextPlain)
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
		SendMessage(context, {"TextPlain": f"{{{proto}{url}}}"})
	# else TODO error message?

def cWeb(context:EventContext, data:InputMessageData) -> None:
	if data.Body:
		try:
			QueryUrl = UrlParse.quote(data.Body)
			Req = HttpReq(f'https://html.duckduckgo.com/html?q={QueryUrl}')
			Caption = f'🦆🔎 "{data.Body}": https://duckduckgo.com/?q={QueryUrl}\n\n'
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
			SendMessage(context, {"TextPlain": f'{Caption}...'})
		except Exception:
			raise
	else:
		pass

def cImages(context:EventContext, data:InputMessageData) -> None:
	pass

def cNews(context:EventContext, data:InputMessageData) -> None:
	pass

def cTranslate(context:EventContext, data:InputMessageData) -> None:
	language_to = data.command.arguments["language_to"]
	text_input = (data.command.body or (data.Quoted and data.Quoted.Body))
	if not (text_input and language_to):
		return SendMessage(context, {"TextPlain": f"Usage: /translate <to language> <text>"})
	try:
		# TODO: Use many different public Lingva instances in rotation to avoid overloading a specific one
		result = json.loads(HttpReq(f'https://lingva.ml/api/v1/auto/{language_to}/{UrlParse.quote(text_input)}').read())
		SendMessage(context, {"TextPlain": f"[{result['info']['detectedSource']} (auto) -> {language_to}]\n\n{result['translation']}"})
	except Exception:
		raise

# unsplash source appears to be deprecated! <https://old.reddit.com/r/unsplash/comments/s13x4h/what_happened_to_sourceunsplashcom/l65epl8/>
def cUnsplash(context:EventContext, data:InputMessageData) -> None:
	try:
		Req = HttpReq(f'https://source.unsplash.com/random/?{UrlParse.quote(data.Body)}')
		ImgUrl = Req.geturl().split('?')[0]
		SendMessage(context, {
			"TextPlain": f'{{{ImgUrl}}}',
			"TextMarkdown": MarkdownCode(ImgUrl, True),
			"Media": Req.read(),
		})
	except Exception:
		raise

def cSafebooru(context:EventContext, data:InputMessageData) -> None:
	ApiUrl = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100&tags='
	try:
		if data.Body:
			for i in range(7): # retry a bunch of times if we can't find a really random result
				ImgUrls = HttpReq(f'{ApiUrl}md5:{RandHexStr(3)}%20{UrlParse.quote(data.Body)}').read().decode().split(' file_url="')[1:]
				if ImgUrls:
					break
			if not ImgUrls: # literal search
				ImgUrls = HttpReq(f'{ApiUrl}{UrlParse.quote(data.Body)}').read().decode().split(' file_url="')[1:]
			if not ImgUrls:
				return SendMessage(context, {"Text": "Error: Could not get any result from Safebooru."})
			ImgXml = choice(ImgUrls)
			ImgUrl = ImgXml.split('"')[0]
			ImgId = ImgXml.split(' id="')[1].split('"')[0]
		else:
			HtmlReq = HttpReq(HttpReq('https://safebooru.org/index.php?page=post&s=random').geturl())
			for Line in HtmlReq.read().decode().replace('\t', ' ').splitlines():
				if '<img ' in Line and ' id="image" ' in Line and ' src="':
					ImgUrl = Line.split(' src="')[1].split('"')[0]
					ImgId = ImgUrl.split('?')[-1]
					break
		if ImgUrl:
			SendMessage(context, {
				"TextPlain": f'[{ImgId}]\n{{{ImgUrl}}}',
				"TextMarkdown": (f'\\[`{ImgId}`\\]\n' + MarkdownCode(ImgUrl, True)),
				"media": {"url": ImgUrl}, #, "bytes": HttpReq(ImgUrl).read()},
			})
		else:
			pass
	except Exception as error:
		raise

RegisterModule(name="Internet", summary="Tools and toys related to the Internet.", endpoints=[
	SafeNamespace(names=["embedded"], summary="Rewrites a link, trying to bypass embed view protection.", handler=cEmbedded),
	SafeNamespace(names=["web"], summary="Provides results of a DuckDuckGo search.", handler=cWeb),
	SafeNamespace(names=["translate"], summary="Returns the received message after translating it in another language.", handler=cTranslate, arguments={
		"language_to": True,
		"language_from": False,
	}),
	#SafeNamespace(names=["unsplash"], summary="Sends a picture sourced from Unsplash.", handler=cUnsplash),
	SafeNamespace(names=["safebooru"], summary="Sends a picture sourced from Safebooru.", handler=cSafebooru),
])

