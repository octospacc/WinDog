# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start #

# MastodonUrl = "https://mastodon.example.com"
# MastodonToken = ""

# end windog config # """

MastodonUrl, MastodonToken = None, None

import mastodon
from bs4 import BeautifulSoup
from magic import Magic

def MastodonMain() -> bool:
	if not (MastodonUrl and MastodonToken):
		return False
	Mastodon = mastodon.Mastodon(api_base_url=MastodonUrl, access_token=MastodonToken)
	class MastodonListener(mastodon.StreamListener):
		def on_notification(self, event):
			MastodonHandler(event)
	Mastodon.stream_user(MastodonListener(), run_async=True)
	return True

def MastodonHandler(event):
	if event['type'] == 'mention':
		#OnMessageParsed()
		message = BeautifulSoup(event['status']['content'], 'html.parser').get_text(' ').strip().replace('\t', ' ')
		if not message.split('@')[0]:
			message = ' '.join('@'.join(message.split('@')[1:]).strip().split(' ')[1:]).strip()
		if message[0] in CmdPrefixes:
			command = ParseCmd(message)
			if command:
				command.messageId = event['status']['id']
				if command.Name in Endpoints:
					CallEndpoint(command.Name, EventContext(platform="mastodon", event=event, manager=Mastodon), command)

def MastodonSender(context:EventContext, data:OutputMessageData, destination) -> None:
	media_results = None
	if data.media:
		media_results = []
		for medium in data.media[:4]: # Mastodon limits posts to 4 attachments
			medium_result = context.manager.media_post(medium, Magic(mime=True).from_buffer(medium))
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

RegisterPlatform(name="Mastodon", main=MastodonMain, sender=MastodonSender, managerClass=mastodon.Mastodon)

