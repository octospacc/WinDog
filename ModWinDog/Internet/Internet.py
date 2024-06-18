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
		result = json.loads(HttpReq(f'https://lingva.ml/api/v1/auto/{toLang}/{UrlParse.quote(toLang.join(data.Body.split(toLang)[1:]))}').read())
		SendMsg(context, {"TextPlain": f"[{result['info']['detectedSource']} (auto) -> {toLang}]\n\n{result['translation']}"})
	except Exception:
		raise

def cUnsplash(context, data) -> None:
	try:
		Req = HttpReq(f'https://source.unsplash.com/random/?{UrlParse.quote(data.Body)}')
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
				ImgUrls = HttpReq(f'{ApiUrl}md5:{RandHexStr(3)}%20{UrlParse.quote(data.Body)}').read().decode().split(' file_url="')[1:]
				if ImgUrls:
					break
			if not ImgUrls: # literal search
				ImgUrls = HttpReq(f'{ApiUrl}{UrlParse.quote(data.Body)}').read().decode().split(' file_url="')[1:]
			if not ImgUrls:
				return SendMsg(context, {"Text": "Error: Could not get any result from Safebooru."})
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
			SendMsg(context, {
				"TextPlain": f'[{ImgId}]\n{{{ImgUrl}}}',
				"TextMarkdown": (f'\\[`{ImgId}`\\]\n' + MarkdownCode(ImgUrl, True)),
				"media": {"url": ImgUrl}, #, "bytes": HttpReq(ImgUrl).read()},
			})
		else:
			pass
	except Exception as error:
		raise

def cDalle(context, data) -> None:
	if not data.Body:
		return SendMsg(context, {"Text": "Please tell me what to generate."})
	image_filter = "&quot;https://th.bing.com/th/id/"
	try:
		retry_index = 3
		result_list = ""
		result_id = HttpReq(
			f"https://www.bing.com/images/create?q={UrlParse.quote(data.Body)}&rt=3&FORM=GENCRE",#"4&FORM=GENCRE",
			body=f"q={UrlParse.urlencode({'q': data.Body})}&qs=ds".encode(),
			headers=MicrosoftBingSettings).read().decode()
		print(result_id)
		result_id = result_id.split('&amp;id=')[1].split('&amp;')[0]
		results_url = f"https://www.bing.com/images/create/-/{result_id}?FORM=GENCRE"
		SendMsg(context, {"Text": "Request sent, please wait..."})
		while retry_index < 12 and image_filter not in result_list:
			result_list = HttpReq(results_url, headers={"User-Agent": MicrosoftBingSettings["User-Agent"]}).read().decode()
			time.sleep(1.25 * retry_index)
			retry_index += 1
		if image_filter in result_list:
			SendMsg(context, {
				"TextPlain": f"{{{results_url}}}",
				"TextMarkdown": MarkdownCode(results_url, True),
				"Media": HttpReq(
					result_list.split(image_filter)[1].split('\\&quot;')[0],
					headers={"User-Agent": MicrosoftBingSettings["User-Agent"]}).read(),
			})
		else:
			raise Exception("Something went wrong.")
	except Exception as error:
		Log(error)
		SendMsg(context, {"TextPlain": error})

RegisterModule(name="Internet", summary="Tools and toys related to the Internet.", endpoints={
	"Embedded": CreateEndpoint(["embedded"], summary="Rewrites a link, trying to bypass embed view protection.", handler=cEmbedded),
	"Web": CreateEndpoint(["web"], summary="Provides results of a DuckDuckGo search.", handler=cWeb),
	"Translate": CreateEndpoint(["translate"], summary="Returns the received message after translating it in another language.", handler=cTranslate),
	"Unsplash": CreateEndpoint(["unsplash"], summary="Sends a picture sourced from Unsplash.", handler=cUnsplash),
	"Safebooru": CreateEndpoint(["safebooru"], summary="Sends a picture sourced from Safebooru.", handler=cSafebooru),
	#"DALL-E": CreateEndpoint(["dalle"], summary="Sends an AI-generated picture from DALL-E 3 via Microsoft Bing.", handler=cDalle),
})

