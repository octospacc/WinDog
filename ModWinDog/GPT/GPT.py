# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import g4f

g4fClient = g4f.client.Client(provider=g4f.Provider.RetryProvider(providers=g4f.providers.any_provider.PROVIERS_LIST_1))

def cGpt(context:EventContext, data:InputMessageData):
	if not (prompt := data.command.body):
		return send_status_400(context, data.user.settings.language)
	output = None
	while not output: # or output.startswith("sorry, 您的ip已由于触发防滥用检测而被封禁,本服务网址是"): # quick fix for a strange ratelimit message
		output = ""
		for completion in g4fClient.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], stream=True):
			output += (completion.choices[0].delta.content or "")
	return send_message(context, {"text_plain": f"[🤖️ GPT]\n\n{output}"})

register_module(name="GPT", endpoints=[
	SafeNamespace(names=["gpt", "chatgpt"], handler=cGpt, body=True),
])

