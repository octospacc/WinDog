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

class EventContext(SafeNamespace):
	pass

class InputMessageData(SafeNamespace):
	pass

class OutputMessageData(SafeNamespace):
	pass

