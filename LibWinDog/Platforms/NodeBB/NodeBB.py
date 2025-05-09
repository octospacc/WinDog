# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start #

# NodeBBUrl = "https://nodebb.example.com"
# NodeBBToken = "abcdefgh-abcd-efgh-ijkl-mnopqrstuvwx"

# end windog config # """

import polling

NodeBBUrl = NodeBBToken = None
NodeBBStamps = {}

def nodebb_request(room_id:int='', method:str="GET", body:dict=None):
	return json.loads(HttpReq(f"{NodeBBUrl}/api/v3/chats/{room_id}", method, headers={
		"Content-Type": "application/json",
		"Authorization": f"Bearer {NodeBBToken}",
	}, body=(body and json.dumps(body).encode())).read().decode())

def NodeBBMain(path:str) -> bool:
	def handler():
		try:
			for room in nodebb_request()["response"]["rooms"]:
				room_id = room["roomId"]
				if "roomId" not in NodeBBStamps:
					NodeBBStamps[room_id] = 0
				if room["teaser"]["timestamp"] > NodeBBStamps[room_id]:
					message = nodebb_request(room_id)["response"]["messages"][-1]
					NodeBBStamps[room_id] = message["timestamp"]
					if not message["self"]:
						text_plain = BeautifulSoup(message["content"]).get_text()
						data = InputMessageData(
							# id = message["timestamp"],
							text_html = message["content"],
							text_plain = text_plain,
							room = SafeNamespace(
								id = room_id,
							),
							user = UserData(
								settings = UserSettingsData(),
							),
							command = TextCommandData(text_plain, "nodebb"),
						)
						on_input_message_parsed(data)
						call_endpoint(EventContext(platform="nodebb"), data)
		except Exception:
			app_log()
	Thread(target=lambda:polling.poll(handler, step=3, poll_forever=True)).start()
	return True

def NodeBBSender(context:EventContext, data:OutputMessageData):
	nodebb_request(context.data.room.id, "POST", {"message": data["text_plain"]})

register_platform(name="NodeBB", main=NodeBBMain, sender=NodeBBSender)