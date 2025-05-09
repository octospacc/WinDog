# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start # """

MicrosoftBingSettings = {}

""" # end windog config # """

from urlextract import URLExtract
from urllib import parse as urlparse
from urllib.request import urlopen, Request
from translate_shell.translate import translate as ts_translate

def RandomHexString(length:int) -> str:
	return ''.join([randchoice('0123456789abcdef') for i in range(length)])

def HttpReq(url:str, method:str|None=None, *, body:bytes=None, headers:dict[str, str]={"User-Agent": WebUserAgent}):
	return urlopen(Request(url, method=method, data=body, headers=headers))

def cEmbedded(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if len(data.command.tokens) >= 2:
		# Find links in command body
		text = (data.text_markdown + ' ' + data.text_plain)
	elif (quoted := data.quoted) and (quoted.text_plain or quoted.text_markdown or quoted.text_html):
		# Find links in quoted message
		text = ((quoted.text_markdown or '') + ' ' + (quoted.text_plain or '') + ' ' + (quoted.text_html or ''))
	else:
		return send_status_400(context, language)
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
		# if urlDomain in ("facebook.com", "www.facebook.com", "m.facebook.com", "mbasic.facebook.com"):
		# 	url = "https://hlb0.octt.eu.org/cors-main.php/https://" + url
		# 	proto = ''
		# else:
		# 	if urlDomain in ("instagram.com", "www.instagram.com"):
		# 		urlDomain = "ddinstagram.com"
		# 	elif urlDomain in ("twitter.com", "x.com"):
		# 		urlDomain = "fxtwitter.com"
		# 	elif urlDomain == "vm.tiktok.com":
		# 		urlDomain = "vm.vxtiktok.com"
		# 	url = (urlDomain + '/' + '/'.join(url.split('/')[1:]))
		if urlDomain.startswith("www."):
			urlDomain = '.'.join(urlDomain.split('.')[1:])
		if urlDomain in ("facebook.com", "m.facebook.com", "instagram.com", "twitter.com", "x.com", "vm.tiktok.com", "tiktok.com", "threads.net", "threads.com"):
			url = f"https://proxatore.octt.eu.org/{url}"
			proto = ''
		elif urlDomain in ("youtube.com",):
			url = f"https://proxatore.octt.eu.org/{url}{'' if url.endswith('?') else '?'}&proxatore-htmlmedia=true&proxatore-mediaproxy=video"
			proto = ''
		return send_message(context, {"text_plain": f"{{{proto}{url}}}"})
	return send_message(context, {"text_plain": "No links found."})

def search_duckduckgo(query:str) -> dict:
	url = f"https://html.duckduckgo.com/html?q={urlparse.quote(query)}"
	request = HttpReq(url)
	results = []
	for line in request.read().decode().replace('\t', ' ').splitlines():
		if ' class="result__a" ' in line and ' href="//duckduckgo.com/l/?uddg=' in line:
			link = urlparse.unquote(line.split(' href="//duckduckgo.com/l/?uddg=')[1].split('&amp;rut=')[0])
			title = line.strip().split('</a>')[0].strip().split('</span>')[-1].strip().split('>')
			if len(title) > 1:
				results.append({"title": html_unescape(title[1].strip()), "link": link})
	return results

def format_search_result(link:str, title:str, index:int) -> str:
	return f'[{index + 1}] {title} : {{{link}}}\n\n'

def cWeb(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not (query := data.command.body):
		return send_status_400(context, language)
	try:
		text = f'🦆🔎 "{query}": https://duckduckgo.com/?q={urlparse.quote(query)}\n\n'
		for i,e in enumerate(search_duckduckgo(query)):
			text += format_search_result(e["link"], e["title"], i)
		return send_message(context, {"text_plain": trim_text(text, 4096, True), "text_mode": "trim"})
	except Exception:
		return send_status_error(context, language)

def cWikipedia(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not (query := data.command.body):
		return send_status_400(context, language)
	try:
		result = search_duckduckgo(f"site:wikipedia.org {query}")[0]
		# TODO try to use API: https://*.wikipedia.org/w/api.php?action=parse&page={title}&prop=text&formatversion=2 (?)
		soup = BeautifulSoup(HttpReq(result["link"]).read().decode(), "html.parser").select('#mw-content-text')[0]
		if len(elems := soup.select('.infobox')):
			elems[0].decompose()
		for elem in soup.select('.mw-editsection'):
			elem.decompose()
		text = (f'{result["title"]}\n{{{result["link"]}}}\n\n' + soup.get_text().strip())
		return send_message(context, {"text_plain": trim_text(text, 4096, True), "text_mode": "trim"})
	except Exception:
		return send_status_error(context, language)

def cFrittoMistoOctoSpacc(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not (query := data.command.body):
		return send_status_400(context, language)
	try:
		query_url = urlparse.quote(query)
		text = f'🍤🔎 "{query}": https://octospacc.altervista.org/?s={query_url}\n\n'
		for i,e in enumerate(json.loads(HttpReq(f"https://octospacc.altervista.org/wp-json/wp/v2/posts?search={query_url}").read().decode())):
			text += format_search_result(e["link"], (e["title"]["rendered"] or e["slug"]), i)
		return send_message(context, {"text_html": trim_text(text, 4096, True), "text_mode": "trim"})
	except Exception:
		return send_status_error(context, language)

def cImages(context:EventContext, data:InputMessageData):
	pass

def cNews(context:EventContext, data:InputMessageData):
	pass

def cTranslate(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	#instances = ["lingva.ml", "lingva.lunar.icu"]
	language_to = data.command.arguments.language_to
	text_input = (data.command.body or (data.quoted and data.quoted.text_plain))
	if not (text_input and language_to):
		return send_status_400(context, language)
	try:
		#result = json.loads(HttpReq(f'https://{randchoice(instances)}/api/v1/auto/{language_to}/{urlparse.quote(text_input)}').read())
		#return send_message(context, {"text_plain": f"[{result['info']['detectedSource']} (auto) -> {language_to}]\n\n{result['translation']}"})
		return send_message(context, {"text_plain": f'[auto -> {language_to}]\n\n{ts_translate(text_input, language_to).results[0].paraphrase}'})
	except Exception:
		return send_status_error(context, language)

# unsplash source appears to be deprecated! <https://old.reddit.com/r/unsplash/comments/s13x4h/what_happened_to_sourceunsplashcom/l65epl8/>
#def cUnsplash(context:EventContext, data:InputMessageData) -> None:
#	try:
#		Req = HttpReq(f'https://source.unsplash.com/random/?{urlparse.quote(data.command.body)}')
#		ImgUrl = Req.geturl().split('?')[0]
#		send_message(context, {
#			"TextPlain": f'{{{ImgUrl}}}',
#			"TextMarkdown": MarkdownCode(ImgUrl, True),
#			"Media": Req.read(),
#		})
#	except Exception:
#		raise

def cSafebooru(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	api_url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit=100&tags='
	try:
		img_id, img_url = None, None
		if (query := data.command.body):
			for i in range(7): # retry a bunch of times if we can't find a really random result
				img_urls = HttpReq(f'{api_url}md5:{RandomHexString(3)}%20{urlparse.quote(query)}').read().decode().split(' file_url="')[1:]
				if img_urls:
					break
			if not img_urls: # literal search
				img_urls = HttpReq(f'{api_url}{urlparse.quote(query)}').read().decode().split(' file_url="')[1:]
			if not img_urls:
				return send_status(context, 404, language, "Could not get any result from Safebooru.", summary=False)
			ImgXml = choice(img_urls)
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
			return send_message(context, OutputMessageData(
				text_plain=f"[{img_id}]\n{{{img_url}}}",
				text_html=f"[<code>{img_id}</code>]\n<pre>{img_url}</pre>",
				media={"url": img_url, "type": "image/"}))
		else:
			return send_status_400(context, language)
	except Exception:
		return send_status_error(context, language)

register_module(name="Internet", endpoints=[
	SafeNamespace(names=["embedded", "embed", "proxy", "proxatore", "sborratore"], handler=cEmbedded, body=False, quoted=False),
	SafeNamespace(names=["web", "search", "duck", "duckduckgo"], handler=cWeb, body=True),
	SafeNamespace(names=["wikipedia", "wokipedia", "wiki"], handler=cWikipedia, body=True),
	SafeNamespace(names=["frittomistodioctospacc", "fmos", "frittomisto", "octospacc"], handler=cFrittoMistoOctoSpacc, body=True),
	SafeNamespace(names=["translate"], handler=cTranslate, body=False, quoted=False, arguments={
		"language_to": True,
		"language_from": False,
	}),
	#SafeNamespace(names=["unsplash"], summary="Sends a picture sourced from Unsplash.", handler=cUnsplash),
	SafeNamespace(names=["safebooru"], handler=cSafebooru, body=False),
])

