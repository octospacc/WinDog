import base64
from binascii import Error as binascii_Error

def mCodings(context:EventContext, data:InputMessageData):
	algorithms = ["base64"]
	methods = {
		"encode_base64": base64.b64encode,
		"decode_base64": base64.b64decode,
		"encode_b64": base64.b64encode,
		"decode_b64": base64.b64decode,
	}
	if (method := ObjGet(methods, f"{data.command.name}_{data.command.arguments.algorithm}")):
		try:
			result = method((data.command.body or (data.quoted and data.quoted.text_plain)).encode()).decode()
			SendMessage(context, {"text_html": f"<pre>{html_escape(result)}</pre>"})
		except binascii_Error:
			SendMessage(context, {"text_plain": f"An error occurred."})
	else:
		language = data.user.settings.language
		SendMessage(context, {
			"text_html": f'{context.endpoint.help_text(language)}\n\n{context.module.get_string("algorithms", language)}: {algorithms}'})

RegisterModule(name="Codings", group="Geek", endpoints=[
	SafeNamespace(names=["encode", "decode"], handler=mCodings, body=False, quoted=False, arguments={
		"algorithm": True,
	}),
])

