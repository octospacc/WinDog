# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start # """

WebConfig = {
	"host": ("0.0.0.0", 30264),
	"url": "https://windog.octt.eu.org",
}

""" # end windog config # """

import queue
from http.server import BaseHTTPRequestHandler
from LibWinDog.Platforms.Web.multithread_http_server import MultiThreadHttpServer

WebQueues = {}

default_css = """<style>
	* { box-sizing: border-box; }
	iframe { width: 100%; height: 3em; top: 0; position: sticky; }
	textarea { width: calc(100% - 3em); height: 2em; }
	input { width: 2em; }
	</style>"""

class WebServerClass(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			uuid = str(time.time())
			WebQueues[uuid] = queue.Queue()
			self.send_response(302)
			self.send_header("Location", f"/{uuid}")
			self.end_headers()
			return
		uuid = self.path.split('/')[-1]
		if self.path.startswith("/form/"):
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=UTF-8")
			self.end_headers()
			self.wfile.write(f'{default_css}<form method="POST" action="/form/{uuid}"><textarea name="text"></textarea><input type="submit" value="📤️"/></form>'.encode())
			return
		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=UTF-8")
		self.send_header("Content-Encoding", "chunked")
		self.end_headers()
		self.wfile.write(f'{default_css}<h3><a href="/">WinDog</a></h3><iframe src="/form/{uuid}"></iframe>'.encode())
		while True: # this apparently makes us lose threads and the web bot becomes unusable, we should handle dropped connections
			try:
				self.wfile.write(("<p>" + WebQueues[uuid].get(block=False).text_html + "</p>").encode())
			except queue.Empty:
				time.sleep(0.01)

	def do_POST(self):
		uuid = self.path.split('/')[-1]
		text = urlparse.unquote_plus(self.rfile.read(int(self.headers["Content-Length"])).decode().split('=')[1])
		self.send_response(302)
		self.send_header("Location", f"/form/{uuid}")
		self.end_headers()
		data = WebMakeInputMessageData(text, uuid)
		OnInputMessageParsed(data)
		call_endpoint(EventContext(platform="web", event=SafeNamespace(room_id=uuid)), data)

def WebMakeInputMessageData(text:str, uuid:str) -> InputMessageData:
	return InputMessageData(
		text_plain = text,
		command = TextCommandData(text, "web"),
		room = SafeNamespace(
			id = f"web:{uuid}",
		),
		user = UserData(
			settings = SafeNamespace(),
		),
	)

def WebMain() -> None:
	server = MultiThreadHttpServer(WebConfig["host"], 32, WebServerClass)
	server.start(background=True)

def WebSender(context:EventContext, data:OutputMessageData) -> None:
	WebQueues[context.event.room_id].put(data)

RegisterPlatform(name="Web", main=WebMain, sender=WebSender)

