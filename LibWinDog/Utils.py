# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from LibWinDog.Types import *

def ObjectUnion(*objects:object, clazz:object=None):
	dikt = {}
	auto_clazz = objects[0].__class__
	for obj in objects:
		if not obj:
			continue
		if type(obj) == dict:
			obj = (clazz or SafeNamespace)(**obj)
		for key, value in tuple(obj.__dict__.items()):
			dikt[key] = value
	return (clazz or auto_clazz)(**dikt)

def ObjectClone(obj:object):
	return ObjectUnion(obj, {});

def SureArray(array:any) -> list|tuple:
	return (array if type(array) in [list, tuple] else [array])

def call_or_return(obj:any, *args) -> any:
	return (obj(*args) if callable(obj) else obj)

def obj_get(node:object, query:str, /) -> any:
	for key in query.split('.'):
		if hasattr(node, "__getitem__") and node.__getitem__:
			# dicts and such
			method = "__getitem__"
			exception = KeyError
		else:
			# namespaces and such
			method = "__getattribute__"
			exception = AttributeError
		try:
			node = node.__getattribute__(method)(key)
		except exception:
			return None
	return node

def strip_url_scheme(url:str) -> str:
	tokens = urlparse.urlparse(url)
	return f"{tokens.netloc}{tokens.path}"

