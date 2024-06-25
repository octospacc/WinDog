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

def MastodonSender(context:EventContext, data:OutputMessageData, destination, textPlain, textMarkdown) -> None:
	if InDict(data, 'Media'):
		Media = context.manager.media_post(data['Media'], Magic(mime=True).from_buffer(data['Media']))
		while Media['url'] == 'null':
			Media = context.manager.media(Media)
	if textPlain or Media:
		context.manager.status_post(
			status=(textPlain + '\n\n@' + context.event['account']['acct']),
			media_ids=(Media if InDict(data, 'Media') else None),
			in_reply_to_id=context.event['status']['id'],
			visibility=('direct' if context.event['status']['visibility'] == 'direct' else 'unlisted'),
		)

RegisterPlatform(name="Mastodon", main=MastodonMain, sender=MastodonSender, managerClass=mastodon.Mastodon)

