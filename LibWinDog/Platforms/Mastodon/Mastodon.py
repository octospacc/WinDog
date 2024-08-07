# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start #

# MastodonUrl = "https://mastodon.example.com"
# MastodonToken = ""

# end windog config # """

MastodonUrl = MastodonToken = None

import mastodon
from bs4 import BeautifulSoup
from magic import Magic

def MastodonMain() -> bool:
	if not (MastodonUrl and MastodonToken):
		return False
	Mastodon = mastodon.Mastodon(api_base_url=MastodonUrl, access_token=MastodonToken)
	class MastodonListener(mastodon.StreamListener):
		def on_notification(self, event):
			MastodonHandler(event, Mastodon)
	Mastodon.stream_user(MastodonListener(), run_async=True)
	return True

def MastodonMakeInputMessageData(status:dict) -> InputMessageData:
	data = InputMessageData(
		message_id = ("mastodon:" + strip_url_scheme(status["uri"])),
		text_html = status["content"],
	)
	data.text_plain = BeautifulSoup(data.text_html, "html.parser").get_text()
	command_tokens = data.text_plain.strip().replace("\t", " ").split(" ")
	while command_tokens[0].strip().startswith('@') or not command_tokens[0]:
		command_tokens.pop(0)
	data.command = ParseCommand(" ".join(command_tokens))
	data.user = UserData(
		id = ("mastodon:" + strip_url_scheme(status["account"]["uri"])),
		name = status["account"]["display_name"],
	)
	data.user.settings = (GetUserSettings(data.user.id) or SafeNamespace())
	return data

def MastodonHandler(event, Mastodon):
	if event["type"] == "mention":
		data = MastodonMakeInputMessageData(event["status"])
		OnMessageParsed(data)
		if (command := ObjGet(data, "command.name")):
			CallEndpoint(command, EventContext(platform="mastodon", event=event, manager=Mastodon), data)

def MastodonSender(context:EventContext, data:OutputMessageData) -> None:
	media_results = None
	if data.media:
		media_results = []
		# TODO support media by url (do we have to upload them or can just pass the original URL?)
		for medium in data.media[:4]: # Mastodon limits posts to 4 attachments, so we drop any more
			medium_result = context.manager.media_post(medium["bytes"], Magic(mime=True).from_buffer(medium["bytes"]))
			while medium_result["url"] == "null":
				medium_result = context.manager.media(medium_result)
			media_results.append(medium_result)
	if data.text_plain or media_results:
		context.manager.status_post(
			status=(data.text_plain + '\n\n@' + context.event['account']['acct']),
			media_ids=media_results,
			in_reply_to_id=context.event['status']['id'],
			visibility=('direct' if context.event['status']['visibility'] == 'direct' else 'unlisted'),
		)

RegisterPlatform(name="Mastodon", main=MastodonMain, sender=MastodonSender, manager_class=mastodon.Mastodon)

