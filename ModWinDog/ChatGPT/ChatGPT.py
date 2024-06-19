# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

from g4f.client import Client as G4FClient

g4fClient = G4FClient()

def cGpt(context:EventContext, data:InputMessageData) -> None:
	if not data.command.body:
		return SendMessage(context, {"Text": "You must type some text."})
	output = ""
	while not output or output.startswith("sorry, 您的ip已由于触发防滥用检测而被封禁,本服务网址是"): # quick fix
		output = ""
		for completion in g4fClient.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": data.command.body}], stream=True):
			output += (completion.choices[0].delta.content or "")
	return SendMessage(context, {"TextPlain": f"[🤖️ GPT]\n\n{output}"})

RegisterModule(name="ChatGPT", endpoints={
	"GPT": CreateEndpoint(["gpt", "chatgpt"], summary="Sends a message to GPT to get back a response. Note: conversations are not yet supported, and this is more standard GPT than ChatGPT, and in general there are many bugs!", handler=cGpt),
})

