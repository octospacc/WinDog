# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

MatrixUrl, MatrixUsername, MatrixPassword = None, None, None

import nio
import simplematrixbotlib as MatrixBotLib
from threading import Thread

def MatrixMain() -> bool:
	if not (MatrixUrl and MatrixUsername and MatrixPassword):
		return False
	MatrixBot = MatrixBotLib.Bot(MatrixBotLib.Creds(MatrixUrl, MatrixUsername, MatrixPassword))
	@MatrixBot.listener.on_message_event
	@MatrixBot.listener.on_custom_event(nio.events.room_events.RoomMessageFile)
	async def MatrixMessageListener(room, message) -> None:
		pass
		#print(message)
		#match = MatrixBotLib.MessageMatch(room, message, MatrixBot)
		#OnMessageReceived()
		#if match.is_not_from_this_bot() and match.command("windogtest"):
		#	pass #await MatrixBot.api.send_text_message(room.room_id, " ".join(arg for arg in match.args()))
	def runMatrixBot() -> None:
		MatrixBot.run()
	Thread(target=runMatrixBot).start()
	return True

def MatrixSender() -> None:
	pass

#RegisterPlatform(name="Matrix", main=MatrixMain, sender=MatrixSender)

