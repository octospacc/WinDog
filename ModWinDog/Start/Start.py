# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cStart(context:EventContext, data:InputMessageData):
	return send_message(context, OutputMessageData(
		text_html=context.endpoint.get_string(
			"start", data.user.settings.language).format(data.user.name)))

register_module(name="Start", endpoints=[
	SafeNamespace(names=["start"], handler=cStart),
])

