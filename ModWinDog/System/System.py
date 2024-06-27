# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import subprocess
from re import compile as re_compile

def cExec(context:EventContext, data:InputMessageData) -> None:
	if not (len(data.command.tokens) >= 2 and data.command.tokens[1].lower() in ExecAllowed):
		return SendMessage(context, {"Text": choice(Locale.__('eval'))})
	command = data.command.tokens[1].lower()
	output = subprocess.run(
		("sh", "-c", f"export PATH=$PATH:/usr/games; {command}"),
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
	# <https://stackoverflow.com/a/14693789>
	text = (re_compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub('', output))
	SendMessage(context, OutputMessageData(
		text_plain=text, text_html=f"<pre>{html_escape(text)}</pre>"))

RegisterModule(name="System", endpoints=[
	SafeNamespace(names=["exec"], handler=cExec),
])

