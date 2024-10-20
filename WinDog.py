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
from sys import exc_info as sys_exc_info
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

def ObjectClone(obj:object):
	return ObjectUnion(obj, {});

def SureArray(array:any) -> list|tuple:
	return (array if type(array) in [list, tuple] else [array])

def app_log(text:str=None, level:str="?", *, newline:bool|None=None, inline:bool=False) -> None:
	if not text:
		text = get_exception_text(full=True)
	endline = '\n'
	if newline == False or (inline and newline == None):
		endline = ''
	text = (str(text) if inline else f"[{level}] [{time.ctime()}] [{int(time.time())}] {text}")
	if LogToConsole:
		print(text, end=endline)
	if LogToFile:
		open((DumpToFile if (DumpToFile and type(DumpToFile) == str) else "./Data/Log.txt"), 'a').write(text + endline)

def get_exception_text(full:bool=False):
	exc_type, exc_value, exc_traceback = sys_exc_info()
	text = f'{exc_type.__qualname__}: {exc_value}'
	if full:
		text = f'@{exc_traceback.tb_frame.f_code.co_name}:{exc_traceback.tb_lineno} {text}'
	return text

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

def good_yaml_load(text:str):
	return yaml_load(text.replace("\t", "    "), Loader=yaml_BaseLoader)

def get_string(bank:dict, query:str, lang:str=None) -> str|list[str]|None:
	if type(result := obj_get(bank, query)) != str:
		if not (result := obj_get(bank, f"{query}.{lang or DefaultLanguage}")):
			if not (result := obj_get(bank, f"{query}.en")):
				result = obj_get(bank, query)
	if result:
		result = result.strip()
	return result

def get_help_text(endpoint, lang:str=None, prefix:str=None) -> str:
	if type(endpoint) == str:
		endpoint = instanciate_endpoint(endpoint, prefix)
	global_string = (lambda query: get_string(GlobalStrings, query, lang))
	text = f'{endpoint.get_string("summary", lang) or ""}\n\n{global_string("usage")}: {prefix or ""}{endpoint.name}'
	if endpoint.arguments:
		for argument in endpoint.arguments:
			if not ((endpoint.body != None) and (endpoint.arguments[argument] == False)):
				argument_help = (endpoint.get_string(f"arguments.{argument}", lang)
					or endpoint.module.get_string(f"arguments.{argument}", lang)
						or argument)
				if endpoint.arguments[argument] == True:
					text += f' &lt;{argument_help}&gt;'
				elif endpoint.arguments[argument] == False:
					text += f' [{argument_help}]'
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
	if (extra := call_or_return(endpoint.help_extra, endpoint, lang)):
		text += f'\n\n{extra}'
	return text

def strip_url_scheme(url:str) -> str:
	tokens = urlparse.urlparse(url)
	return f"{tokens.netloc}{tokens.path}"

def parse_command_arguments(command, endpoint, count:int=None):
	arguments = SafeNamespace()
	body = command.body
	index = 1
	for key in (endpoint.arguments or range(count)):
		if (not count) and (endpoint.body != None) and (endpoint.arguments[key] == False):
			continue # skip optional (False) arguments for now if command expects a body, they will be implemented later
		try:
			value = command.tokens[index]
			body = body[len(value):].strip()
		except IndexError:
			value = None
		arguments[str(key)] = value
		index += 1
	return [arguments, body]

def TextCommandData(text:str, platform:str) -> CommandData|None:
	if not text:
		return None
	text = text.strip()
	try: # ensure text is non-empty and an actual command
		if not (text[0] in CommandPrefixes and text[1:].strip()):
			return None
	except IndexError:
		return None
	command = SafeNamespace()
	command.tokens = text.split()
	command.prefix = command.tokens[0][0]
	command.name, command_target = (command.tokens[0][1:].lower().split('@') + [''])[:2]
	if command_target and not (command_target == call_or_return(Platforms[platform].agent_info).tag.lower()):
		return None
	command.body = text[len(command.tokens[0]):].strip()
	if not (endpoint := obj_get(Endpoints, command.name)):
		return command # TODO shouldn't this return None?
	command.parse_arguments = (lambda count=None: parse_command_arguments(command, endpoint, count))
	if endpoint.arguments:
		[command.arguments, command.body] = command.parse_arguments()
	return command

def on_input_message_parsed(data:InputMessageData) -> None:
	dump_message(data, prefix='> ')
	handle_bridging(send_message, data, from_sent=False)
	update_user_db(data.user)

def on_output_message_sent(output_data:OutputMessageData, input_data:InputMessageData, from_sent:bool) -> None:
	if (not from_sent) and input_data:
		output_data = ObjectUnion(output_data, {"room": input_data.room})
	dump_message(output_data, prefix=f'<{"*" if from_sent else " "}')
	if not from_sent:
		handle_bridging(send_message, output_data, from_sent=True)

def handle_bridging(method:callable, data:MessageData, from_sent:bool):
	if data.user:
		if (text_plain := obj_get(data, "text_plain")):
			text_plain = f"<{data.user.name}>: {text_plain}"
		if (text_html := obj_get(data, "text_html")):
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

def check_bot_admin(data:InputMessageData|UserData) -> bool:
	user = (data.user or data)
	return ((user.id in AdminIds) or (user.tag in AdminIds))

# TODO make this real
def check_room_admin(data:InputMessageData|UserData) -> bool:
	return check_bot_admin(data)

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
		open((DumpToFile if (DumpToFile and type(DumpToFile) == str) else "./Data/Dump.txt"), 'a').write(text + '\n')

def send_status(context:EventContext, code:int, lang:str=None, extra:str=None, preamble:bool=True, summary:bool=True):
	global_string = (lambda query: get_string(GlobalStrings, query, lang))
	summary_text = (global_string(f"statuses.{code}.summary") or '')
	return send_message(context, {"text_html": (
		(((f'{global_string(f"statuses.{code}.icon")} {global_string("error") if code >= 400 else ""}'.strip()
			+ f' {code}: {global_string(f"statuses.{code}.title")}. {summary_text if summary else ""}').strip()) if preamble else '')
				+ '\n\n' + (extra or "")).strip()})

def send_status_400(context:EventContext, lang:str=None, extra:str=None):
	return send_status(context, 400, lang,
		f'{context.endpoint.get_help_text(lang)}\n\n{extra or ""}', preamble=False, summary=False)

def send_status_error(context:EventContext, lang:str=None, code:int=500, extra:str=None):
	result = send_status(context, code, lang,
		f'{html_escape(get_exception_text())}\n\n{extra or ""}')
	app_log()
	return result

def send_message(context:EventContext, data:OutputMessageData, *, from_sent:bool=False):
	context = ObjectClone(context)
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
	on_output_message_sent(data, context.data, from_sent)
	return result

def send_notice(context:EventContext, data):
	...

def edit_message(context:EventContext, data:MessageData):
	...

def delete_message(context:EventContext, data:MessageData):
	...

def register_platform(name:str, main:callable, sender:callable, linker:callable=None, *, event_class=None, manager_class=None, agent_info=None) -> None:
	Platforms[name.lower()] = SafeNamespace(name=name, main=main, sender=sender, linker=linker, event_class=event_class, manager_class=manager_class, agent_info=agent_info)
	app_log(f"{name}, ", inline=True)

def register_module(name:str, endpoints:dict, *, group:str|None=None) -> None:
	module = SafeNamespace(group=group, endpoints=endpoints, get_string=(lambda query, lang=None: None))
	if isfile(file := f"./ModWinDog/{name}/{name}.yaml"):
		module.strings = good_yaml_load(open(file, 'r').read())
		module.get_string = (lambda query, lang=None: get_string(module.strings, query, lang))
	Modules[name] = module
	if group not in ModuleGroups:
		ModuleGroups[group] = []
	ModuleGroups[group].append(name)
	app_log(f"{name}, ", inline=True)
	for endpoint in endpoints:
		endpoint.module = module
		for name in endpoint.names:
			Endpoints[name] = endpoint

def instanciate_endpoint(name:str, prefix:str):
	if not (endpoint := obj_get(Endpoints, name)):
		return None
	endpoint = ObjectClone(endpoint)
	endpoint.name = name
	endpoint.get_string = (lambda query=name, lang=None:
		endpoint.module.get_string(f"endpoints.{name}.{query}", lang))
	endpoint.get_help_text = (lambda lang=None: get_help_text(endpoint, lang, prefix))
	return endpoint

def call_endpoint(context:EventContext, data:InputMessageData):
	if not ((command := data.command) and (name := command.name)):
		return
	if not (endpoint := instanciate_endpoint(name, command.prefix)):
		return
	context.data = data
	context.module = endpoint.module
	context.endpoint = endpoint
	if callable(agent_info := Platforms[context.platform].agent_info):
		Platforms[context.platform].agent_info = agent_info()
	return endpoint.handler(context, data)

def write_new_config() -> None:
	app_log("💾️ No configuration found! Generating and writing to `./Data/Config.py`... ", inline=True)
	with open("./Data/Config.py", 'w') as configFile:
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

def app_main() -> None:
	#SetupDb()
	app_log(f"📨️ Initializing Platforms... ", newline=False)
	for platform in Platforms.values():
		if platform.main(f"./LibWinDog/Platforms/{platform.name}"):
			app_log(f"{platform.name}, ", inline=True)
	app_log("...Done. ✅️", inline=True, newline=True)
	app_log("🐶️ WinDog Ready!")
	while True:
		time.sleep(9**9)

if __name__ == '__main__':
	app_log("🌞️ WinDog Starting...")
	GlobalStrings = good_yaml_load(open("./WinDog.yaml", 'r').read())
	Platforms, Modules, ModuleGroups, Endpoints = {}, {}, {}, {}

	for folder in ("LibWinDog/Platforms", "ModWinDog"):
		match folder:
			case "LibWinDog/Platforms":
				app_log("📩️ Loading Platforms... ", newline=False)
			case "ModWinDog":
				app_log("🔩️ Loading Modules... ", newline=False)
		for name in listdir(f"./{folder}"):
			path = f"./{folder}/{name}"
			if path.endswith(".py") and isfile(path):
				exec(open(path).read())
			elif isdir(path):
				files = listdir(path)
				if f"{name}.py" in files:
					files.remove(f"{name}.py")
					exec(open(f"{path}/{name}.py", 'r').read())
				#for file in files:
				#	if file.endswith(".py"):
				#		exec(open(f"{path}/{file}", 'r').read())
		app_log("...Done. ✅️", inline=True, newline=True)

	app_log("💽️ Loading Configuration... ", newline=False)
	if isfile("./Data/Config.py"):
		exec(open("./Data/Config.py", 'r').read())
	else:
		write_new_config()
	app_log("Done. ✅️", inline=True, newline=True)

	app_main()
	app_log("🌚️ WinDog Stopping...")

