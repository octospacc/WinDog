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

from asyncio import run as asyncio_run
import nio
#from nio import AsyncClient, MatrixRoom, RoomMessageText
#import simplematrixbotlib as MatrixBotLib

async def MatrixMessageHandler(room:nio.MatrixRoom, event:nio.RoomMessage) -> None:
	data = MatrixMakeInputMessageData(room, event)

def MatrixMakeInputMessageData(room:nio.MatrixRoom, event:nio.RoomMessage) -> InputMessageData:
	data = InputMessageData(
		message_id = f"matrix:{event.event_id}",
		room = SafeNamespace(
			id = f"matrix:{room.room_id}",
			name = room.display_name,
		),
		user = SafeNamespace(
			id = f"matrix:{event.sender}",
		)
	)
	print(data)
	return data

def MatrixMain() -> bool:
	if not (MatrixUrl and MatrixUsername and (MatrixPassword or MatrixToken)):
		return False
	#MatrixBot = MatrixBotLib.Bot(MatrixBotLib.Creds(MatrixUrl, MatrixUsername, MatrixPassword))
	##@MatrixBot.listener.on_message_event
	#@MatrixBot.listener.on_custom_event(nio.RoomMessageText)
	#async def MatrixMessageListener(room, message, event) -> None:
	#	print(message)
	#	#match = MatrixBotLib.MessageMatch(room, message, MatrixBot)
	#	#OnMessageParsed()
	#	#if match.is_not_from_this_bot() and match.command("windogtest"):
	#	#	pass #await MatrixBot.api.send_text_message(room.room_id, " ".join(arg for arg in match.args()))
	#@MatrixBot.listener.on_custom_event(nio.RoomMessageFile)
	#async def MatrixMessageFileListener(room, event):
	#	print(event)
	#Thread(target=lambda:MatrixBot.run()).start()
	async def client() -> None:
		client = nio.AsyncClient(MatrixUrl, MatrixUsername)
		login = await client.login(password=MatrixPassword, token=MatrixToken)
		if MatrixPassword and (not MatrixToken) and (token := ObjGet(login, "access_token")):
			open("./Config.py", 'a').write(f'\n# Added automatically #\nMatrixToken = "{token}"\n')
		await client.sync(30000) # resync old messages first to "skip read ones"
		client.add_event_callback(MatrixMessageHandler, nio.RoomMessage)
		await client.sync_forever(timeout=30000)
	Thread(target=lambda:asyncio_run(client())).start()
	return True

def MatrixSender() -> None:
	pass

#RegisterPlatform(name="Matrix", main=MatrixMain, sender=MatrixSender)

