# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

from types import SimpleNamespace

class DictNamespace(SimpleNamespace):
	def __iter__(self):
		return self.__dict__.__iter__()
	def __getitem__(self, key):
		return self.__getattribute__(key)
	def __setitem__(self, key, value):
		return self.__setattr__(key, value)

class SafeNamespace(DictNamespace):
	def __getattribute__(self, key):
		try:
			return super().__getattribute__(key)
		except AttributeError:
			return None

# we just use these for type hinting and clearer code:

class EventContext(SafeNamespace):
	pass

class UserData(SafeNamespace):
	pass

class MessageData(SafeNamespace):
	pass

class InputMessageData(MessageData):
	pass

class OutputMessageData(MessageData):
	pass

