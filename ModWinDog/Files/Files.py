
def cListFiles(context:EventContext, data:InputMessageData):
	files = []
	for file in File.select().where(File.owner == data.user.id):
		files.append(file.path)
	return send_message(context, {"text_plain": str(files)})

def cReadFile(context:EventContext, data:InputMessageData):
	text = read_db_file(data.user.id, data.command.arguments.path)
	return send_message(context, {"text_html": f'<pre>{text}</pre>'})

@require_bot_admin
def cWriteFile(context:EventContext, data:InputMessageData):
	update_or_create(File, {"owner": data.user.id, "path": data.command.arguments.path}, {"content": data.command.body.encode("utf-8")})

def cDeleteFile(context:EventContext, data:InputMessageData):
	File.delete().where((File.owner == data.user.id) & (File.path == data.command.arguments.path)).execute()

register_module(name="Files", endpoints=[
	SafeNamespace(names=["listfiles"], handler=cListFiles),
	SafeNamespace(names=["readfile"], handler=cReadFile, arguments={"path": True}),
	SafeNamespace(names=["writefile"], handler=cWriteFile, arguments={"path": True}, body=False, quoted=False),
	SafeNamespace(names=["deletefile"], handler=cDeleteFile, arguments={"path": True}),
])