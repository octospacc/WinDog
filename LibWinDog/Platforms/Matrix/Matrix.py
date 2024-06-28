# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start #

# MatrixUrl = "https://matrix.example.com"
# MatrixUsername = "username"

# Provide either your password, or an active access_token below.
# MatrixPassword = "hunter2"

# If logging in via password, a token will be automatically generated and saved to Config.
# MatrixToken = ""

# end windog config # """

MatrixUrl, MatrixUsername, MatrixPassword, MatrixToken = None, None, None, None
MatrixClient = None

from asyncio import run as asyncio_run, create_task as asyncio_create_task
import nio

def MatrixMain() -> bool:
	if not (MatrixUrl and MatrixUsername and (MatrixPassword or MatrixToken)):
		return False
	def upgrade_username(new:str):
		global MatrixUsername
		MatrixUsername = new
	async def client_main() -> None:
		global MatrixClient
		MatrixClient = nio.AsyncClient(MatrixUrl, MatrixUsername)
		login = await MatrixClient.login(password=MatrixPassword, token=MatrixToken)
		if MatrixPassword and (not MatrixToken) and (token := ObjGet(login, "access_token")):
			open("./Config.py", 'a').write(f'\n# Added automatically #\nMatrixToken = "{token}"\n')
		if (bot_id := ObjGet(login, "user_id")):
			upgrade_username(bot_id) # ensure username is fully qualified for the API
		await MatrixClient.sync(30000) # resync old messages first to "skip read ones"
		MatrixClient.add_event_callback(MatrixMessageHandler, nio.RoomMessage)
		await MatrixClient.sync_forever(timeout=30000)
	Thread(target=lambda:asyncio_run(client_main())).start()
	return True

def MatrixMakeInputMessageData(room:nio.MatrixRoom, event:nio.RoomMessage) -> InputMessageData:
	data = InputMessageData(
		message_id = f"matrix:{event.event_id}",
		datetime = event.server_timestamp,
		text_plain = event.body,
		text_html = event.formatted_body, # note: this could be None
		room = SafeNamespace(
			id = f"matrix:{room.room_id}",
			name = room.display_name,
		),
		user = SafeNamespace(
			id = f"matrix:{event.sender}",
			#name = , # TODO name must be get via a separate API request (and so maybe we should cache it)
		),
	)
	data.command = ParseCommand(data.text_plain)
	data.user.settings = (GetUserSettings(data.user.id) or SafeNamespace())
	return data

async def MatrixMessageHandler(room:nio.MatrixRoom, event:nio.RoomMessage) -> None:
	if MatrixUsername == event.sender:
		return # ignore messages that come from the bot itself
	data = MatrixMakeInputMessageData(room, event)
	OnMessageParsed(data)
	if (command := ObjGet(data, "command.name")):
		CallEndpoint(command, EventContext(platform="matrix", event=SafeNamespace(room=room, event=event), manager=MatrixClient), data)

def MatrixSender(context:EventContext, data:OutputMessageData, destination) -> None:
	asyncio_create_task(context.manager.room_send(room_id=context.event.room.room_id, message_type="m.room.message", content={"msgtype": "m.text", "body": data.text_plain}))

RegisterPlatform(name="Matrix", main=MatrixMain, sender=MatrixSender)

