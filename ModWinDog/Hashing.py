# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import hashlib

def cHash(context, data) -> None:
	if len(data.Tokens) >= 3 and data.Tokens[1] in hashlib.algorithms_available:
		Alg = data.Tokens[1]
		Hash = hashlib.new(Alg, Alg.join(data.Body.split(Alg)[1:]).strip().encode()).hexdigest()
		SendMsg(context, {
			"TextPlain": Hash,
			"TextMarkdown": MarkdownCode(Hash, True),
		})
	else:
		SendMsg(context, {"Text": choice(Locale.__('hash.usage')).format(data.Tokens[0], hashlib.algorithms_available)})

RegisterModule(name="Hashing", group="Geek", summary="Functions for hashing of textual content.", endpoints={
	"Hash": CreateEndpoint(["hash"], summary="Responds with the hash-sum of a message received.", handler=cHash),
})

