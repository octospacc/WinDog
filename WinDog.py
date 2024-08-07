#!/usr/bin/env python3
# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import json, time
from glob import glob
from hashlib import new as hashlib_new
from html import escape as html_escape, unescape as html_unescape
from os import listdir
from os.path import isfile, isdir
from random import choice, choice as randchoice, randint
from threading import Thread
from traceback import format_exc, format_exc as traceback_format_exc
from urllib import parse as urlparse, parse as urllib_parse
from yaml import load as yaml_load, BaseLoader as yaml_BaseLoader
from bs4 import BeautifulSoup
from LibWinDog.Types import *
from LibWinDog.Config import *
from LibWinDog.Database import *

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

def Log(text:str, level:str="?", *, newline:bool|None=None, inline:bool=False) -> None:
	endline = '\n'
	if newline == False or (inline and newline == None):
		endline = ''
	text = (text if inline else f"[{level}] [{time.ctime()}] [{int(time.time())}] {text}")
	if LogToConsole:
		print(text, end=endline)
	if LogToFile:
		open("./Log.txt", 'a').write(text + endline)

def call_or_return(obj:any) -> any:
	return (obj() if callable(obj) else obj)

def SureArray(array:any) -> list|tuple:
	return (array if type(array) in [list, tuple] else [array])

def ObjGet(node:object, query:str, /) -> any:
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

def good_yaml_load(text:str):
	return yaml_load(text.replace("\t", "    "), Loader=yaml_BaseLoader)

def get_string(bank:dict, query:str|dict, lang:str=None) -> str|list[str]|None:
	if not (result := ObjGet(bank, f"{query}.{lang or DefaultLanguage}")):
		if not (result := ObjGet(bank, f"{query}.en")):
			result = ObjGet(bank, query)
	return result

def help_text(endpoint, lang:str=None) -> str:
	global_string = (lambda query: get_string(GlobalStrings, query, lang))
	text = f'{endpoint.get_string("summary", lang) or ""}\n\n{global_string("usage")}:'
	if endpoint.arguments:
		for argument in endpoint.arguments:
			if endpoint.arguments[argument]:
				text += f' &lt;{endpoint.get_string(f"arguments.{argument}", lang) or endpoint.module.get_string(f"arguments.{argument}", lang) or argument}&gt;'
	body_help = (endpoint.get_string("body", lang) or endpoint.module.get_string("body", lang))
	quoted_help = (global_string("quoted_message") + (f': {body_help}' if body_help else ''))
	if not body_help:
		body_help = global_string("text")
	if endpoint.body == False and endpoint.quoted == False:
		text += f' &lt;{global_string("text")} {global_string("or")} {global_string("quoted_message")}: {body_help}&gt;'
	else:
		if endpoint.body == True:
			text += f' &lt;{body_help}&gt;'
		elif endpoint.body == False:
			text += f' [{body_help}]'
		if endpoint.quoted == True:
			text += f' &lt;{quoted_help}&gt;'
		elif endpoint.quoted == False:
			text += f' [{quoted_help}]'
	return text

def strip_url_scheme(url:str) -> str:
	tokens = urlparse.urlparse(url)
	return f"{tokens.netloc}{tokens.path}"

def RandPercent() -> int:
	num = randint(0,100)
	return (f'{num}.00' if num == 100 else f'{num}.{randint(0,9)}{randint(0,9)}')

def RandHexStr(length:int) -> str:
	hexa = ''
	for char in range(length):
		hexa += choice('0123456789abcdef')
	return hexa

def GetUserSettings(user_id:str) -> SafeNamespace|None:
	try:
		return SafeNamespace(**EntitySettings.select().join(User).where(User.id == user_id).dicts().get())
	except EntitySettings.DoesNotExist:
		return None

def ParseCommand(text:str, platform:str) -> SafeNamespace|None:
	if not text:
		return None
	text = text.strip()
	try: # ensure text is a non-empty command
		if not (text[0] in CmdPrefixes and text[1:].strip()):
			return None
	except IndexError:
		return None
	command = SafeNamespace()
	command.tokens = text.split()
	command.name, command_target = (command.tokens[0][1:].lower().split('@') + [''])[:2]
	if command_target and not (command_target == call_or_return(Platforms[platform].agent_info).tag.lower()):
		return None
	command.body = text[len(command.tokens[0]):].strip()
	if command.name not in Endpoints:
		return command
	if (endpoint_arguments := Endpoints[command.name].arguments):
		command.arguments = SafeNamespace()
		index = 1
		for key in endpoint_arguments:
			if not endpoint_arguments[key]:
				continue # skip optional (False) arguments for now, they will be implemented later
			try:
				value = command.tokens[index]
				command.body = command.body[len(value):].strip()
			except IndexError:
				value = None
			command.arguments[key] = value
			index += 1
	return command

def OnInputMessageParsed(data:InputMessageData) -> None:
	dump_message(data, prefix='> ')
	handle_bridging(SendMessage, data, from_sent=False)
	update_user_db(data.user)

def OnOutputMessageSent(output_data:OutputMessageData, input_data:InputMessageData, from_sent:bool) -> None:
	if (not from_sent) and input_data:
		output_data = ObjectUnion(output_data, {"room": input_data.room})
	dump_message(output_data, prefix=f'<{"*" if from_sent else " "}')
	if not from_sent:
		handle_bridging(SendMessage, output_data, from_sent=True)

# TODO: fix to send messages to different rooms, this overrides destination data but that gives problems with rebroadcasting the bot's own messages
def handle_bridging(method:callable, data:MessageData, from_sent:bool):
	if data.user:
		if (text_plain := ObjGet(data, "text_plain")):
			text_plain = f"<{data.user.name}>: {text_plain}"
		if (text_html := ObjGet(data, "text_html")):
			text_html = (urlparse.quote(f"<{data.user.name}>: ") + text_html)
	for bridge in BridgesConfig:
		if data.room.id not in bridge:
			continue
		rooms = list(bridge)
		rooms.remove(data.room.id)
		for room_id in rooms:
			method(
				SafeNamespace(platform=room_id.split(':')[0]),
				ObjectUnion(data, {"room": SafeNamespace(id=room_id)}, ({"text_plain": text_plain, "text_markdown": None, "text_html": text_html} if data.user else None)),
				from_sent=True)

def update_user_db(user:SafeNamespace) -> None:
	if not (user and user.id):
		return
	try:
		User.get(User.id == user.id)
	except User.DoesNotExist:
		user_hash = ("sha256:" + hashlib_new("sha256", user.id.encode()).hexdigest())
		try:
			User.get(User.id_hash == user_hash)
			User.update(id=user.id).where(User.id_hash == user_hash).execute()
		except User.DoesNotExist:
			User.create(id=user.id, id_hash=user_hash)

def dump_message(data:InputMessageData, prefix:str='') -> None:
	if not (Debug and (DumpToFile or DumpToConsole)):
		return
	text = (data.text_plain.replace('\n', '\\n') if data.text_plain else '')
	text = f"{prefix} [{int(time.time())}] [{time.ctime()}] [{data.room and data.room.id}] [{data.message_id}] [{data.user and data.user.id}] {text}"
	if DumpToConsole:
		print(text, data)
	if DumpToFile:
		open((DumpToFile if (DumpToFile and type(DumpToFile) == str) else "./Dump.txt"), 'a').write(text + '\n')

def SendMessage(context:EventContext, data:OutputMessageData, from_sent:bool=False) -> None:
	data = (OutputMessageData(**data) if type(data) == dict else data)
	if data.text_html and not data.text_plain:
		data.text_plain = BeautifulSoup(data.text_html, "html.parser").get_text()
	elif data.text_markdown and not data.text_plain:
		data.text_plain = data.text_markdown
	elif data.text_plain and not data.text_html:
		data.text_html = html_escape(data.text_plain)
	if data.media:
		data.media = SureArray(data.media)
	if data.room and (room_id := data.room.id):
		tokens = room_id.split(':')
		if tokens[0] != context.platform:
			context.platform = tokens[0]
			context.manager = context.event = None
		data.room.id = ':'.join(tokens[1:])
	if data.ReplyTo: # TODO decide if this has to be this way
		data.ReplyTo = ':'.join(data.ReplyTo.split(':')[1:])
	if context.platform not in Platforms:
		return None
	platform = Platforms[context.platform]
	if (not context.manager) and (manager := platform.manager_class):
		context.manager = call_or_return(manager)
	result = platform.sender(context, data)
	OnOutputMessageSent(data, context.data, from_sent)
	return result

def SendNotice(context:EventContext, data) -> None:
	pass

def DeleteMessage(context:EventContext, data) -> None:
	pass

def RegisterPlatform(name:str, main:callable, sender:callable, linker:callable=None, *, event_class=None, manager_class=None, agent_info=None) -> None:
	Platforms[name.lower()] = SafeNamespace(name=name, main=main, sender=sender, linker=linker, event_class=event_class, manager_class=manager_class, agent_info=agent_info)
	Log(f"{name}, ", inline=True)

def RegisterModule(name:str, endpoints:dict, *, group:str|None=None) -> None:
	module = SafeNamespace(group=group, endpoints=endpoints, get_string=(lambda query, lang=None: None))
	if isfile(file := f"./ModWinDog/{name}/{name}.yaml"):
		module.strings = good_yaml_load(open(file, 'r').read())
		module.get_string = (lambda query, lang=None: get_string(module.strings, query, lang))
	Modules[name] = module
	Log(f"{name}, ", inline=True)
	for endpoint in endpoints:
		endpoint.module = module
		for name in endpoint.names:
			Endpoints[name] = endpoint

def CallEndpoint(name:str, context:EventContext, data:InputMessageData):
	endpoint = Endpoints[name]
	context.data = data
	context.module = endpoint.module
	context.endpoint = endpoint
	context.endpoint.get_string = (lambda query=data.command.name, lang=None:
		endpoint.module.get_string(f"endpoints.{data.command.name}.{query}", lang))
	context.endpoint.help_text = (lambda lang=None: help_text(endpoint, lang))
	if callable(agent_info := Platforms[context.platform].agent_info):
		Platforms[context.platform].agent_info = agent_info()
	return endpoint.handler(context, data)

def WriteNewConfig() -> None:
	Log("💾️ No configuration found! Generating and writing to `./Config.py`... ", inline=True)
	with open("./Config.py", 'w') as configFile:
		opening = '# windog config start #'
		closing = '# end windog config #'
		for folder in ("LibWinDog", "ModWinDog"):
			for file in glob(f"./{folder}/**/*.py", recursive=True):
				try:
					name = '/'.join(file.split('/')[1:-1])
					heading = f"# ==={'=' * len(name)}=== #"
					source = open(file, 'r').read().replace(f"''' {opening}", f'""" {opening}').replace(f"{closing} '''", f'{closing} """')
					content = '\n'.join(content.split(f'""" {opening}')[1].split(f'{closing} """')[0].split('\n')[1:-1])
					configFile.write(f"{heading}\n# 🔽️ {name} 🔽️ #\n{heading}\n{content}\n\n")
				except IndexError:
					pass

def Main() -> None:
	#SetupDb()
	Log(f"📨️ Initializing Platforms... ", newline=False)
	for platform in Platforms.values():
		if platform.main():
			Log(f"{platform.name}, ", inline=True)
	Log("...Done. ✅️", inline=True, newline=True)
	Log("🐶️ WinDog Ready!")
	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	Log("🌞️ WinDog Starting...")
	GlobalStrings = good_yaml_load(open("./WinDog.yaml", 'r').read())
	Platforms, Modules, ModuleGroups, Endpoints = {}, {}, {}, {}

	for folder in ("LibWinDog/Platforms", "ModWinDog"):
		match folder:
			case "LibWinDog/Platforms":
				Log("📩️ Loading Platforms... ", newline=False)
			case "ModWinDog":
				Log("🔩️ Loading Modules... ", newline=False)
		for name in listdir(f"./{folder}"):
			path = f"./{folder}/{name}"
			if isfile(path):
				exec(open(path, 'r').read())
			elif isdir(path):
				files = listdir(path)
				if f"{name}.py" in files:
					files.remove(f"{name}.py")
					exec(open(f"{path}/{name}.py", 'r').read())
				for file in files:
					if file.endswith(".py"):
						exec(open(f"{path}/{name}.py", 'r').read())
		Log("...Done. ✅️", inline=True, newline=True)

	Log("💽️ Loading Configuration... ", newline=False)
	from Config import *
	if isfile("./Config.py"):
		from Config import *
	else:
		WriteNewConfig()
	Log("Done. ✅️", inline=True, newline=True)

	Main()
	Log("🌚️ WinDog Stopping...")

