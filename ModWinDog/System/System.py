# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start # """

# False: ASCII output; True: ANSI Output (must be escaped)
ExecAllowed = {"date": False, "fortune": False, "neofetch": True, "uptime": False}

""" # end windog config # """

import subprocess
from re import compile as re_compile

def cExec(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not (len(data.command.tokens) >= 2):
		return send_status_400(context, language)
	if not data.command.tokens[1].lower() in ExecAllowed:
		return send_status(context, 404, language, context.endpoint.get_string("statuses.404", language), summary=False)
	command = data.command.tokens[1].lower()
	output = subprocess.run(
		("sh", "-c", f"export PATH=$PATH:/usr/games; {command}"),
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
	# <https://stackoverflow.com/a/14693789>
	text = (re_compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub('', output))
	return send_message(context, {"text_html": f'<pre>{html_escape(text)}</pre>'})

@require_bot_admin
def cRestart(context:EventContext, data:InputMessageData):
	open("./.WinDog.Restart.lock", 'w').close()
	return send_message(context, {"text_plain": "Bot restart queued."})

register_module(name="System", endpoints=[
	SafeNamespace(names=["exec"], handler=cExec, body=True),
	SafeNamespace(names=["restart"], handler=cRestart),
])

