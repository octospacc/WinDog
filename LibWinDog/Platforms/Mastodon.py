import mastodon

def MastodonSender(event, manager, Data, Destination, TextPlain, TextMarkdown) -> None:
	if InDict(Data, 'Media'):
		Media = manager.media_post(Data['Media'], Magic(mime=True).from_buffer(Data['Media']))
		while Media['url'] == 'null':
			Media = manager.media(Media)
	if TextPlain:
		manager.status_post(
			status=(TextPlain + '\n\n@' + event['account']['acct']),
			media_ids=(Media if InDict(Data, 'Media') else None),
			in_reply_to_id=event['status']['id'],
			visibility=('direct' if event['status']['visibility'] == 'direct' else 'unlisted'),
		)

# TODO make this non-blocking or else we can't load it dynamically
def MastodonMain() -> None:
	if not (MastodonUrl and MastodonToken):
		return
	Mastodon = mastodon.Mastodon(api_base_url=MastodonUrl, access_token=MastodonToken)
	class MastodonListener(mastodon.StreamListener):
		def on_notification(self, event):
			if event['type'] == 'mention':
				Msg = BeautifulSoup(event['status']['content'], 'html.parser').get_text(' ').strip().replace('\t', ' ')
				if not Msg.split('@')[0]:
					Msg = ' '.join('@'.join(Msg.split('@')[1:]).strip().split(' ')[1:]).strip()
				if Msg[0] in CmdPrefixes:
					Cmd = ParseCmd(Msg)
					Cmd.messageId = event['status']['id']
					if Cmd.Name in Endpoints:
						Endpoints[Cmd.Name]({"Event": event, "Manager": Mastodon}, Cmd)
	Mastodon.stream_user(MastodonListener())

Platforms["Mastodon"] = {"main": MastodonMain, "sender": MastodonSender, "managerClass": mastodon.Mastodon}
