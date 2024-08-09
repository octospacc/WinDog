# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from json import dumps as json_dumps

# TODO work with links to messages
def cDump(context:EventContext, data:InputMessageData):
	if not (message := data.quoted):
		return send_status_400(context, data.user.settings.language)
	text = json_dumps(message, default=(lambda obj: obj.__dict__), indent="  ")
	return send_message(context, {"text_html": f'<pre>{html_escape(text)}</pre>'})

RegisterModule(name="Dumper", group="Geek", endpoints=[
	SafeNamespace(names=["dump"], handler=cDump, quoted=True),
])

