# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start # """

WebConfig = {
	"host": ("0.0.0.0", 30264),
	"url": "https://windog.octt.eu.org",
	"anti_drop_interval": 15,
}

""" # end windog config # """

import queue
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread
from uuid6 import uuid7

WebQueues = {}
web_css_style = web_js_script = None
web_html_prefix = (lambda document_class='', head_extra='': (f'''<!DOCTYPE html><html class="{document_class}"><head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>WinDog 🐶️</title>
<link rel="stylesheet" href="/windog.css"/>
<script src="/windog.js">''' + '' + f'''</script>
{head_extra}</head><body>'''))

class WebServerClass(BaseHTTPRequestHandler):
	def parse_path(self):
		path = self.path.strip('/').lower()
		try:
			query = path.split('?')[1].split('&')
		except Exception:
			query = []
		path = path.split('?')[0]
		return (path, path.split('/'), query)

	def do_redirect(self, path:str):
		self.send_response(302)
		self.send_header("Location", path)
		self.end_headers()

	def send_text_content(self, text:str, mime:str, infinite:bool=False):
		self.send_response(200)
		self.send_header("Content-Type", f"{mime}; charset=UTF-8")
		self.end_headers()
		self.wfile.write(text.encode())
		if infinite:
			while True:
				time.sleep(9**9)

	def init_new_room(self, room_id:str=None):
		if not room_id:
			room_id = str(uuid7().hex)
		WebQueues[room_id] = {}
		#WebPushEvent(room_id, ".start", self.headers)
		#Thread(target=lambda:WebAntiDropEnqueue(room_id)).start()
		self.do_redirect(f"/{room_id}")

	def handle_room_chat(self, room_id:str, user_id:str, is_redirected:bool=False):
		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=UTF-8")
		self.send_header("Content-Encoding", "chunked")
		self.end_headers()
		if not is_redirected:
			target = f"/{room_id}/{user_id}?page-target=1#load-target"
			self.wfile.write(f'''{web_html_prefix(head_extra=f'<meta http-equiv="refresh" content="0; url={target}">')}
<h3><a href="/" target="_parent">WinDog 🐶️</a></h3>
<p>Initializing... <a href="{target}">Click here</a> if you are not automatically redirected.</p>'''.encode())
		else:
			self.wfile.write(f'''{web_html_prefix()}
<h3><a href="/" target="_parent">WinDog 🐶️</a></h3>
<div class="sticky-box">
<p id="load-target" style="display: none;"><span style="color: red;">Background loading seems to have stopped...</span> Please open a new chat or <a href="/{room_id}">reload this current one</a> if you can't send new messages.</p>
<div class="input-frame"><iframe src="/form/{room_id}/{user_id}"></iframe></div>
</div>
<div style="display: flex; flex-direction: column-reverse;">'''.encode())
			while True:
				# TODO this apparently makes us lose threads, we should handle dropped connections?
				try:
					self.wfile.write(WebMakeMessageHtml(WebQueues[room_id][user_id].get(block=False), user_id).encode())
				except queue.Empty:
					time.sleep(0.01)

	def send_form_html(self, room_id:str, user_id:str):
		self.send_text_content((f'''{web_html_prefix("form no-margin")}
<!--<link rel="stylesheet" href="/on-connection-dropped.css"/>-->
<!--<p class="on-connection-dropped">Connection dropped! Please <a href="/" target="_parent">open a new chat</a>.</p>-->
<form method="POST" action="/form/{room_id}/{user_id}" onsubmit="''' + '''(function(event){
	var textEl = event.target.querySelector('[name=\\'text\\']');
	textEl.value = textEl.value.trim();
	window.parent.inputFrameResize();
	if (!textEl.value) {
		event.preventDefault();
	}
})(event);''' + '''">
<textarea name="text" required="true" autofocus="true" placeholder="Type something..." onkeydown="''' + '''(function(event){
	var submitOnEnterSimple = !event.shiftKey;
	var submitOnEnterCombo = (event.shiftKey || event.ctrlKey);
	if ((event.keyCode === 13) && submitOnEnterCombo) {
		event.preventDefault();
		event.target.parentElement.querySelector('input[type=\\'submit\\']').click();
	}
})(event);''' + '''" oninput="window.parent.inputFrameResize();"></textarea>
<!--<input type="text" name="text" required="true" autofocus="true" placeholder="Type something..."/>-->
<input type="submit" value="📤️"/>
</form>'''), "text/html")

	def do_GET(self):
		room_id = user_id = None
		path, fields, query = self.parse_path()
		if not path:
			self.init_new_room()
		elif path == "windog.css":
			self.send_text_content(web_css_style, "text/css")
		#elif path == "on-connection-dropped.css":
		#	self.send_text_content('.on-connection-dropped { display: revert; } form { display: none; }', "text/css", infinite=True)
		elif path == "windog.js":
			self.send_text_content(web_js_script, "application/javascript")
		elif fields[0] == "api":
			... # TODO rest API
		elif fields[0] == "form":
			self.send_form_html(*fields[1:3])
		else:
			room_id, user_id = (fields + [None])[0:2]
			if room_id not in WebQueues:
				self.init_new_room(room_id if (len(room_id) >= 32) else None)
			if user_id:
				if user_id not in WebQueues[room_id]:
					WebQueues[room_id][user_id] = queue.Queue()
					WebPushEvent(room_id, user_id, ".start", self.headers)
					Thread(target=lambda:WebAntiDropEnqueue(room_id, user_id)).start()
				self.handle_room_chat(room_id, user_id, ("page-target=1" in query))
			else:
				self.send_text_content(f'''{web_html_prefix("wrapper no-margin")}<iframe src="/{room_id}/{uuid7().hex}#load-target"></iframe>''', "text/html")

	def do_POST(self):
		path, fields, query = self.parse_path()
		if path and fields[0] == 'form':
			room_id, user_id = fields[1:3]
			self.send_form_html(room_id, user_id)
			WebPushEvent(room_id, user_id, urlparse.unquote_plus(self.rfile.read(int(self.headers["Content-Length"])).decode().split('=')[1]), self.headers)

def WebPushEvent(room_id:str, user_id:str, text:str, headers:dict[str:str]):
	context = EventContext(platform="web", event=SafeNamespace(room_id=room_id, user_id=user_id))
	data = InputMessageData(
		text_plain = text,
		text_html = html_escape(text),
		command = TextCommandData(text, "web"),
		room = SafeNamespace(
			id = f"web:{room_id}",
		),
		user = UserData(
			id = f"web:{user_id}",
			name = ("User" + str(abs(hash('\n'.join([f"{key}: {headers[key]}" for key in headers if key.lower() in ["accept", "accept-language", "accept-encoding", "dnt", "user-agent"]]))) % (10**8))),
			settings = UserSettingsData(),
		),
	)
	on_input_message_parsed(data)
	WebSender(context, ObjectUnion(data, {"from_user": True}))
	call_endpoint(context, data)

def WebMakeMessageHtml(message:MessageData, for_user_id:str):
	if not (message.text_html or message.media):
		return "<!---->"
	user_id = (message.user and message.user.id and message.user.id.split(':')[1])
	# NOTE: this doesn't handle tags with attributes!
	if message.text_html and (f"{message.text_html}<".split('>')[0].split('<')[1] not in ['p', 'pre']):
		message.text_html = f'<p>{message.text_html}</p>'
	return (f'<div class="message {"from-self" if (user_id == for_user_id) else ""} {f"color-{(int(user_id, 16) % 6) + 1}" if (user_id and (user_id != for_user_id)) else ""}">'
		+ f'<span class="name">{(message.user and message.user.name) or "WinDog"}</span>'
		+ (message.text_html.replace('\n', "<br />") if message.text_html else '')
		+ (''.join([f'<p><img src="{medium.url}"/></p>' for medium in message.media]) if message.media else '')
	+ '</div>')

def WebMain(path:str) -> bool:
	global web_css_style, web_js_script
	web_css_style = open(f"{path}/windog.css", 'r').read()
	web_js_script = open(f"{path}/windog.js", 'r').read()
	Thread(target=lambda:ThreadingHTTPServer(WebConfig["host"], WebServerClass).serve_forever()).start()
	return True

def WebSender(context:EventContext, data:OutputMessageData) -> None:
	for user_id in (room := WebQueues[context.event.room_id]):
		room[user_id].put(data)

# prevent browser from closing connection after ~1 minute of inactivity, by continuously sending empty, invisible messages
# TODO maybe there should exist only a single thread with this function handling all queues? otherwise we're probably wasting many threads!
def WebAntiDropEnqueue(room_id:str, user_id:str):
	while True:
		WebQueues[room_id][user_id].put(OutputMessageData())
		time.sleep(WebConfig["anti_drop_interval"])

register_platform(name="Web", main=WebMain, sender=WebSender)

