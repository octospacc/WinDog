# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

from json import dumps as json_dumps

def cDump(context:EventContext, data:InputMessageData):
	if (message := data.quoted):
		dump_text = json_dumps(message, default=(lambda obj: obj.__dict__), indent="  ")
	SendMessage(context, {
		"text_html": (f'<pre>{html_escape(dump_text)}</pre>' if message
			else context.endpoint.help_text(data.user.settings.language))})

RegisterModule(name="Dumper", group="Geek", endpoints=[
	SafeNamespace(names=["dump"], handler=cDump, quoted=True),
])

