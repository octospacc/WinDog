# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

from types import SimpleNamespace

class SafeNamespace(SimpleNamespace):
	def __getattribute__(self, value):
		try:
			return super().__getattribute__(value)
		except AttributeError:
			return None

# we just use these for type hinting:

class EventContext(SafeNamespace):
	pass

class MessageData(SafeNamespace):
	pass

class InputMessageData(MessageData):
	pass

class OutputMessageData(MessageData):
	pass

