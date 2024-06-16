# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

from urlextract import URLExtract
from urllib import parse as UrlParse
from urllib.request import urlopen, Request

def HttpGet(url:str):
	return urlopen(Request(url, headers={"User-Agent": WebUserAgent}))

def cEmbedded(context, data) -> None:
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
		SendMsg(context, {"TextPlain": f"{{{proto}{url}}}"})
	# else TODO error message?

def cWeb(context, data) -> None:
	if data.Body:
		try:
			QueryUrl = UrlParse.quote(data.Body)
			Req = HttpGet(f'https://html.duckduckgo.com/html?q={QueryUrl}')
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
			SendMsg(context, {"TextPlain": f'{Caption}...'})
		except Exception:
			raise
	else:
		pass

def cImages(context, data) -> None:
	pass

def cNews(context, data) -> None:
	pass

def cTranslate(context, data) -> None:
	if len(data.Tokens) < 3:
		return
	try:
		toLang = data.Tokens[1]
		# TODO: Use many different public Lingva instances in rotation to avoid overloading a specific one
		result = json.loads(HttpGet(f'https://lingva.ml/api/v1/auto/{toLang}/{UrlParse.quote(toLang.join(data.Body.split(toLang)[1:]))}').read())
		SendMsg(context, {"TextPlain": f"[{result['info']['detectedSource']} (auto) -> {toLang}]\n\n{result['translation']}"})
	except Exception:
		raise

def cUnsplash(context, data) -> None:
	try:
		Req = HttpGet(f'https://source.unsplash.com/random/?{UrlParse.quote(data.Body)}')
		ImgUrl = Req.geturl().split('?')[0]
		SendMsg(context, {
			"TextPlain": f'{{{ImgUrl}}}',
			"TextMarkdown": MarkdownCode(ImgUrl, True),
			"Media": Req.read(),
		})
	except Exception:
		raise

def cSafebooru(context, data) -> None:
	ApiUrl = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100&tags='
	try:
		if data.Body:
			for i in range(7): # retry a bunch of times if we can't find a really random result
				ImgUrls = HttpGet(f'{ApiUrl}md5:{RandHexStr(3)}%20{UrlParse.quote(data.Body)}').read().decode().split(' file_url="')[1:]
				if ImgUrls:
					break
			if not ImgUrls: # literal search
				ImgUrls = HttpGet(f'{ApiUrl}{UrlParse.quote(data.Body)}').read().decode().split(' file_url="')[1:]
			if not ImgUrls:
				return SendMsg(context, {"Text": "Error: Could not get any result from Safebooru."})
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
			SendMsg(context, {
				"TextPlain": f'[{ImgId}]\n{{{ImgUrl}}}',
				"TextMarkdown": (f'\\[`{ImgId}`\\]\n' + MarkdownCode(ImgUrl, True)),
				"Media": HttpGet(ImgUrl).read(),
			})
		else:
			pass
	except Exception:
		raise

RegisterModule(name="Internet", summary="Tools and toys related to the Internet.", endpoints={
	"Embedded": CreateEndpoint(["embedded"], summary="Rewrites a link, trying to bypass embed view protection.", handler=cEmbedded),
	"Web": CreateEndpoint(["web"], summary="Provides results of a DuckDuckGo search.", handler=cWeb),
	"Translate": CreateEndpoint(["translate"], summary="Returns the received message after translating it in another language.", handler=cTranslate),
	"Unsplash": CreateEndpoint(["unsplash"], summary="Sends a picture sourced from Unsplash.", handler=cUnsplash),
	"Safebooru": CreateEndpoint(["safebooru"], summary="Sends a picture sourced from Safebooru.", handler=cSafebooru),
})

