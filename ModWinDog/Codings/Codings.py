# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

import base64
import base256

CodingsAlgorithms = []
CodingsMethods = {
	"encode:ascii85": base64.a85encode,
	"decode:ascii85": base64.a85decode,
	"encode:base16": base64.b16encode,
	"decode:base16": base64.b16decode,
	"encode:base32": base64.b32encode,
	"decode:base32": base64.b32decode,
	"encode:base32hex": base64.b32hexencode,
	"decode:base32hex": base64.b32hexdecode,
	"encode:base64": base64.b64encode,
	"decode:base64": base64.b64decode,
	"encode:base85": base64.b85encode,
	"decode:base85": base64.b85decode,
	"encode:base256": (lambda decoded: base256.encode_string(decoded.decode()).encode()),
	"decode:base256": (lambda encoded: base256.decode_string(encoded.decode()).encode()),
}
for method in dict(CodingsMethods):
	method2 = method.replace("ascii", 'a').replace("base", 'b')
	CodingsMethods[method2] = CodingsMethods[method]
	if (name := method.split(':')[1]) not in CodingsAlgorithms:
		CodingsAlgorithms.append(name)

def mCodings(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	method = obj_get(CodingsMethods, f"{data.command.name}:{data.command.arguments.algorithm}")
	text = (data.command.body or (data.quoted and data.quoted.text_plain))
	if not (method and text):
		return send_status_400(context, language)
	try:
		return send_message(context, {
			"text_html": f"<pre>{html_escape(method(text.encode()).decode())}</pre>"})
	except Exception:
		return send_status_error(context, language)

register_module(name="Codings", group="Geek", endpoints=[
	SafeNamespace(names=["encode", "decode"], handler=mCodings, body=False, quoted=False, arguments={
		"algorithm": True,
	}, help_extra=(lambda endpoint, lang: f'{endpoint.module.get_string("algorithms", lang)}: <code>{"</code>, <code>".join(CodingsAlgorithms)}</code>.')),
])

