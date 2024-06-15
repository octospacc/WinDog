# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

# If you have modified the bot's code, you should set this
ModifiedSourceUrl = ''

MastodonUrl = ''
MastodonToken = ''

TelegramId = 1637713483
TelegramToken = ''
TelegramAdmins = [ 123456789, ]
TelegramWhitelist = [ 123456789, ]
TelegramRestrict = False

AdminIds = [ "123456789@telegram", "admin@activitypub@mastodon.example.com", ]

DefaultLang = 'en'
Debug = False
Dumper = False
CmdPrefixes = '.!/'
# False: ASCII output; True: ANSI Output (must be escaped)
ExecAllowed = {'date': False, 'fortune': False, 'neofetch': True, 'uptime': False}
WebUserAgent = f'WinDog v.Staging'

Endpoints = {
	"start": cStart,
	"help": cHelp,
	#"config": cConfig,
	"source": cSource,
	"ping": cPing,
	"echo": cEcho,
	"broadcast": cBroadcast,
	#"repeat": cRepeat,
	"wish": percenter,
	"level": percenter,
	"hug": multifun,
	"pat": multifun,
	"poke": multifun,
	"cuddle": multifun,
	"floor": multifun,
	"hands": multifun,
	"sessocto": multifun,
	"hash": cHash,
	#"encode": cEncode,
	#"decode": cDecode,
	#"time": cTime,
	"eval": cEval,
	"exec": cExec,
	#"format": cFormat,
	#"frame": cFrame,
	"embedded": cEmbedded,
	"web": cWeb,
	"translate": cTranslate,
	"unsplash": cUnsplash,
	"safebooru": cSafebooru,
}
