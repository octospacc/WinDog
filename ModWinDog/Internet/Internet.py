# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start # """

MicrosoftBingSettings = {}

""" # end windog config # """

from urlextract import URLExtract
from urllib.request import urlopen, Request

def HttpReq(url:str, method:str|None=None, *, body:bytes=None, headers:dict[str, str]={"User-Agent": WebUserAgent}):
	return urlopen(Request(url, method=method, data=body, headers=headers))

def cEmbedded(context:EventContext, data:InputMessageData) -> None:
	if len(data.command.tokens) >= 2:
		# Find links in command body
		text = (data.text_markdown + ' ' + data.text_plain)
	elif (quoted := data.quoted) and (quoted.text_plain or quoted.text_markdown or quoted.text_html):
		# Find links in quoted message
		text = ((quoted.text_markdown or '') + ' ' + (quoted.text_plain or '') + ' ' + (quoted.text_html or ''))
	else:
		# TODO Error message
		return
	pass
	urls = URLExtract().find_urls(text)
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
			if urlDomain in ("instagram.com", "www.instagram.com"):
				urlDomain = "ddinstagram.com"
			elif urlDomain in ("twitter.com", "x.com"):
				urlDomain = "fxtwitter.com"
			elif urlDomain == "vm.tiktok.com":
				urlDomain = "vm.vxtiktok.com"
			url = (urlDomain + '/' + '/'.join(url.split('/')[1:]))
		SendMessage(context, {"text_plain": f"{{{proto}{url}}}"})
	# else TODO error message?

def cWeb(context:EventContext, data:InputMessageData) -> None:
	if not (query := data.command.body):
		return # TODO show message
	try:
		QueryUrl = urlparse.quote(query)
		Req = HttpReq(f'https://html.duckduckgo.com/html?q={QueryUrl}')
		Caption = f'🦆🔎 "{query}": https://duckduckgo.com/?q={QueryUrl}\n\n'
		Index = 0
		for Line in Req.read().decode().replace('\t', ' ').splitlines():
			if ' class="result__a" ' in Line and ' href="//duckduckgo.com/l/?uddg=' in Line:
				Index += 1
				Link = urlparse.unquote(Line.split(' href="//duckduckgo.com/l/?uddg=')[1].split('&amp;rut=')[0])
				Title = Line.strip().split('</a>')[0].strip().split('</span>')[-1].strip().split('>')
				if len(Title) > 1:
					Title = html_unescape(Title[1].strip())
					Caption += f'[{Index}] {Title} : {{{Link}}}\n\n'
				else:
					continue
		SendMessage(context, {"TextPlain": f'{Caption}...'})
	except Exception:
		raise

def cImages(context:EventContext, data:InputMessageData) -> None:
	pass

def cNews(context:EventContext, data:InputMessageData) -> None:
	pass

def cTranslate(context:EventContext, data:InputMessageData) -> None:
	instances = ["lingva.ml", "lingva.lunar.icu"]
	language_to = data.command.arguments["language_to"]
	text_input = (data.command.body or (data.quoted and data.quoted.text_plain))
	if not (text_input and language_to):
		return SendMessage(context, {"TextPlain": f"Usage: /translate <to language> <text>"})
	try:
		result = json.loads(HttpReq(f'https://{randchoice(instances)}/api/v1/auto/{language_to}/{urlparse.quote(text_input)}').read())
		SendMessage(context, {"TextPlain": f"[{result['info']['detectedSource']} (auto) -> {language_to}]\n\n{result['translation']}"})
	except Exception:
		raise

# unsplash source appears to be deprecated! <https://old.reddit.com/r/unsplash/comments/s13x4h/what_happened_to_sourceunsplashcom/l65epl8/>
#def cUnsplash(context:EventContext, data:InputMessageData) -> None:
#	try:
#		Req = HttpReq(f'https://source.unsplash.com/random/?{urlparse.quote(data.command.body)}')
#		ImgUrl = Req.geturl().split('?')[0]
#		SendMessage(context, {
#			"TextPlain": f'{{{ImgUrl}}}',
#			"TextMarkdown": MarkdownCode(ImgUrl, True),
#			"Media": Req.read(),
#		})
#	except Exception:
#		raise

def cSafebooru(context:EventContext, data:InputMessageData) -> None:
	ApiUrl = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100&tags='
	try:
		img_id, img_url = None, None
		if (query := data.command.body):
			for i in range(7): # retry a bunch of times if we can't find a really random result
				ImgUrls = HttpReq(f'{ApiUrl}md5:{RandHexStr(3)}%20{urlparse.quote(query)}').read().decode().split(' file_url="')[1:]
				if ImgUrls:
					break
			if not ImgUrls: # literal search
				ImgUrls = HttpReq(f'{ApiUrl}{urlparse.quote(query)}').read().decode().split(' file_url="')[1:]
			if not ImgUrls:
				return SendMessage(context, {"Text": "Error: Could not get any result from Safebooru."})
			ImgXml = choice(ImgUrls)
			img_url = ImgXml.split('"')[0]
			img_id = ImgXml.split(' id="')[1].split('"')[0]
		else:
			HtmlReq = HttpReq(HttpReq('https://safebooru.org/index.php?page=post&s=random').geturl())
			for Line in HtmlReq.read().decode().replace('\t', ' ').splitlines():
				if '<img ' in Line and ' id="image" ' in Line and ' src="':
					img_url = Line.split(' src="')[1].split('"')[0]
					img_id = img_url.split('?')[-1]
					break
		if img_url:
			SendMessage(context, OutputMessageData(
				text_plain=f"[{img_id}]\n{{{img_url}}}",
				text_html=f"[<code>{img_id}</code>]\n<pre>{img_url}</pre>",
				media={"url": img_url}))
		else:
			pass
	except Exception as error:
		raise

RegisterModule(name="Internet", endpoints=[
	SafeNamespace(names=["embedded"], handler=cEmbedded),
	SafeNamespace(names=["web"], handler=cWeb),
	SafeNamespace(names=["translate"], handler=cTranslate, arguments={
		"language_to": True,
		"language_from": False,
	}),
	#SafeNamespace(names=["unsplash"], summary="Sends a picture sourced from Unsplash.", handler=cUnsplash),
	SafeNamespace(names=["safebooru"], handler=cSafebooru),
])

