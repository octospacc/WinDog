# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

import hashlib

def cHash(context:EventContext, data:InputMessageData) -> None:
	algorithm = data.command.arguments["algorithm"]
	if data.command.body and algorithm in hashlib.algorithms_available:
		hashed = hashlib.new(algorithm, data.command.body.encode()).hexdigest()
		SendMessage(context, {
			"TextPlain": hashed,
			"TextMarkdown": MarkdownCode(hashed, True),
		})
	else:
		SendMessage(context, {"Text": choice(Locale.__('hash.usage')).format(data.command.tokens[0], hashlib.algorithms_available)})

RegisterModule(name="Hashing", group="Geek", summary="Functions for hashing of textual content.", endpoints={
	"Hash": CreateEndpoint(names=["hash"], summary="Responds with the hash-sum of a message received.", handler=cHash, arguments={
		"algorithm": True,
	}),
})

