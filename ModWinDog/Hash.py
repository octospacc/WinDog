import hashlib

# Module: Hash
# Responds with the hash-sum of a message received.
def cHash(Context, Data) -> None:
	if len(Data.Tokens) >= 3 and Data.Tokens[1] in hashlib.algorithms_available:
		Alg = Data.Tokens[1]
		Hash = hashlib.new(Alg, Alg.join(Data.Body.split(Alg)[1:]).strip().encode()).hexdigest()
		SendMsg(Context, {
			"TextPlain": Hash,
			"TextMarkdown": MarkdownCode(Hash, True),
		})
	else:
		SendMsg(Context, {"Text": choice(Locale.__('hash.usage')).format(Data.Tokens[0], hashlib.algorithms_available)})

