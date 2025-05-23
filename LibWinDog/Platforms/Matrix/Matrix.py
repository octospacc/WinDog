# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start #

# MatrixUrl = "https://matrix.example.com"
# MatrixUsername = "username"

# Provide either your password, or an active access_token below.
# MatrixPassword = "hunter2"

# If logging in via password, a token will be automatically generated and saved to Config.
# MatrixToken = ""

# end windog config # """

MatrixUrl = MatrixUsername = MatrixPassword = MatrixToken = None

import asyncio
import nio
import queue

MatrixClient = None
MatrixQueue = queue.Queue()

def MatrixMain(path:str) -> bool:
	if not (MatrixUrl and MatrixUsername and (MatrixPassword or MatrixToken)):
		return False
	def upgrade_username(new:str):
		global MatrixUsername
		MatrixUsername = new
	async def queue_handler():
		asyncio.ensure_future(queue_handler())
		try:
			MatrixSender(*MatrixQueue.get(block=False))
		except queue.Empty:
			time.sleep(0.01) # avoid 100% CPU usage ☠️
	async def client_main() -> None:
		global MatrixClient
		MatrixClient = nio.AsyncClient(MatrixUrl, MatrixUsername)
		login = await MatrixClient.login(password=MatrixPassword, token=MatrixToken)
		if MatrixPassword and (not MatrixToken) and (token := obj_get(login, "access_token")):
			open("./Config.py", 'a').write(f'\n# Added automatically #\nMatrixToken = "{token}"\n')
		if (bot_id := obj_get(login, "user_id")):
			upgrade_username(bot_id) # ensure username is fully qualified for the API
		await MatrixClient.sync(30000) # resync old messages first to "skip read ones"
		asyncio.ensure_future(queue_handler())
		MatrixClient.add_event_callback(MatrixMessageHandler, nio.RoomMessage)
		MatrixClient.add_event_callback(MatrixInviteHandler, nio.InviteEvent)
		await MatrixClient.sync_forever(timeout=30000)
	Thread(target=lambda:asyncio.run(client_main())).start()
	return True

def MatrixMakeInputMessageData(room:nio.MatrixRoom, event:nio.RoomMessage) -> InputMessageData:
	data = InputMessageData(
		message_id = f"matrix:{event.event_id}",
		timestamp = event.server_timestamp,
		text_plain = event.body,
		text_html = obj_get(event, "formatted_body"), # this could be unavailable
		media = ({"url": event.url} if obj_get(event, "url") else None),
		room = SafeNamespace(
			id = f"matrix:{room.room_id}",
			name = room.display_name,
		),
		user = UserData(
			id = f"matrix:{event.sender}",
			#name = , # TODO name must be get via a separate API request (and so maybe we should cache it)
		),
	)
	if (mxc_url := obj_get(data, "media.url")) and mxc_url.startswith("mxc://"):
		_, _, server_name, media_id = mxc_url.split('/')
		data.media["url"] = ("https://" + server_name + nio.Api.download(server_name, media_id)[1])
	data.command = TextCommandData(data.text_plain, "matrix")
	data.user.settings = UserSettingsData(data.user.id)
	return data

async def MatrixInviteHandler(room:nio.MatrixRoom, event:nio.InviteEvent) -> None:
	await MatrixClient.join(room.room_id)

async def MatrixMessageHandler(room:nio.MatrixRoom, event:nio.RoomMessage) -> None:
	if MatrixUsername == event.sender:
		return # ignore messages that come from the bot itself
	data = MatrixMakeInputMessageData(room, event)
	on_input_message_parsed(data)
	call_endpoint(EventContext(platform="matrix", event=SafeNamespace(room=room, event=event), manager=MatrixClient), data)

def MatrixSender(context:EventContext, data:OutputMessageData):
	try:
		asyncio.get_event_loop()
	except RuntimeError:
		MatrixQueue.put((context, data))
		return None
	asyncio.create_task(context.manager.room_send(
		room_id=((data.room and data.room.id) or obj_get(context, "event.room.room_id")),
		message_type="m.room.message",
		content={"msgtype": "m.text", "body": data.text_plain}))

register_platform(name="Matrix", main=MatrixMain, sender=MatrixSender, manager_class=(lambda:MatrixClient))

