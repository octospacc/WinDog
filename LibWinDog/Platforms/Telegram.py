import telegram, telegram.ext
from telegram import ForceReply, Bot
from telegram.utils.helpers import escape_markdown
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

def TelegramCmdAllowed(update:telegram.Update) -> bool:
	if not TelegramRestrict:
		return True
	if TelegramRestrict.lower() == 'whitelist':
		if update.message.chat.id in TelegramWhitelist:
			return True
	return False

def TelegramHandleCmd(update:telegram.Update):
	TelegramQueryHandle(update)
	if TelegramCmdAllowed(update):
		return ParseCmd(update.message.text)
	else:
		return False

def TelegramQueryHandle(update:telegram.Update, context:CallbackContext=None) -> None:
	if not (update and update.message):
		return
	Cmd = ParseCmd(update.message.text)
	Cmd.messageId = update.message.message_id
	Cmd.TextPlain = Cmd.Body
	Cmd.TextMarkdown = update.message.text_markdown_v2
	Cmd.Text = GetWeightedText((Cmd.TextMarkdown, Cmd.TextPlain))
	if Cmd and Cmd.Tokens[0][0] in CmdPrefixes and Cmd.Name in Endpoints:
		Cmd.User = {
			"Name": update.message.from_user.first_name,
			"Tag": update.message.from_user.username,
			"Id": f'{update.message.from_user.id}@telegram',
		}
		if update.message.reply_to_message:
			Cmd.Quoted = SimpleNamespace(**{
				"messageId": update.message.reply_to_message.message_id,
				"Body": update.message.reply_to_message.text,
				"TextPlain": update.message.reply_to_message.text,
				"TextMarkdown": update.message.reply_to_message.text_markdown_v2,
				"Text": GetWeightedText((update.message.reply_to_message.text_markdown_v2, update.message.reply_to_message.text)),
				"User": {
					"Name": update.message.reply_to_message.from_user.first_name,
					"Tag": update.message.reply_to_message.from_user.username,
					"Id": f'{update.message.reply_to_message.from_user.id}@telegram',
				},
			})
		Endpoints[Cmd.Name]({"Event": update, "Manager": context}, Cmd)
	if Debug and Dumper:
		Text = update.message.text
		Text = (Text.replace('\n', '\\n') if Text else '')
		with open('Dump.txt', 'a') as File:
			File.write(f'[{time.ctime()}] [{int(time.time())}] [{update.message.chat.id}] [{update.message.message_id}] [{update.message.from_user.id}] {Text}\n')

def TelegramSender(event, manager, Data, Destination, TextPlain, TextMarkdown) -> None:
	if Destination:
		manager.bot.send_message(Destination, text=TextPlain)
	else:
		replyToId = (Data["ReplyTo"] if ("ReplyTo" in Data and Data["ReplyTo"]) else event.message.message_id)
		if InDict(Data, 'Media'):
			event.message.reply_photo(
				Data['Media'],
				caption=(TextMarkdown if TextMarkdown else TextPlain if TextPlain else None),
				parse_mode=('MarkdownV2' if TextMarkdown else None),
				reply_to_message_id=replyToId,
			)
		elif TextMarkdown:
			event.message.reply_markdown_v2(TextMarkdown, reply_to_message_id=replyToId)
		elif TextPlain:
			event.message.reply_text(TextPlain, reply_to_message_id=replyToId)

def TelegramMain() -> None:
	if not TelegramToken:
		return
	updater = telegram.ext.Updater(TelegramToken)
	dispatcher = updater.dispatcher
	#dispatcher.add_handler(CommandHandler('config', cConfig))
	dispatcher.add_handler(MessageHandler(Filters.text | Filters.command, TelegramQueryHandle))
	updater.start_polling()

Platforms["Telegram"] = {"main": TelegramMain, "sender": TelegramSender, "eventClass": telegram.Update}
