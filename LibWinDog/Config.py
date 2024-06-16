# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

# If you have modified the bot's code, you should set this
ModifiedSourceUrl = ""

# Only for the platforms you want to use, uncomment the below credentials and fill with your own:

# MastodonUrl = "https://mastodon.example.com"
# MastodonToken = ""

# MatrixUrl = "https://matrix.example.com"
# MatrixUsername = "username"
# MatrixPassword = "hunter2"

# TelegramToken = "1234567890:abcdefghijklmnopqrstuvwxyz123456789"

AdminIds = [ "123456789@telegram", "634314973@telegram", "admin@activitypub@mastodon.example.com", ]

DefaultLang = "en"
Debug = False
Dumper = False
CmdPrefixes = ".!/"
# False: ASCII output; True: ANSI Output (must be escaped)
ExecAllowed = {"date": False, "fortune": False, "neofetch": True, "uptime": False}
WebUserAgent = "WinDog v.Staging"

ModuleGroups = (ModuleGroups | {
	"Basic": "",
	"Geek": "",
})

