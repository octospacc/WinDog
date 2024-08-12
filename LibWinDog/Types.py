# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from types import SimpleNamespace

class DictNamespace(SimpleNamespace):
	def __init__(self, **kwargs):
		for key in kwargs:
			if type(kwargs[key]) == dict:
				kwargs[key] = self.__class__(**kwargs[key])
		return super().__init__(**kwargs)
	def __iter__(self):
		return self.__dict__.__iter__()
	def __getitem__(self, key):
		return self.__getattribute__(key)
	def __setitem__(self, key, value):
		return self.__setattr__(key, value)
	#def __setattr__(self, key, value):
		#if type(value) == dict:
			#value = self.__class__(**value)
		#return super().__setattr__(key, value)

class SafeNamespace(DictNamespace):
	def __getattribute__(self, key):
		try:
			return super().__getattribute__(key)
		except AttributeError:
			return None

# we just use these for type hinting and clearer code:

class CommandData(SafeNamespace):
	pass

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

