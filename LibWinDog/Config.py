# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #
""" # windog config start # """

# If you have modified the bot's code, you should set this
ModifiedSourceUrl = ""

LogToConsole = True
LogToFile = True

DumpToConsole = False
DumpToFile = False

AdminIds = [ "123456789@telegram", "634314973@telegram", "admin@activitypub@mastodon.example.com", ]

DefaultLang = "en"
Debug = False
CmdPrefixes = ".!/"
# False: ASCII output; True: ANSI Output (must be escaped)
ExecAllowed = {"date": False, "fortune": False, "neofetch": True, "uptime": False}
WebUserAgent = "WinDog v.Staging"

#ModuleGroups = (ModuleGroups | {
ModuleGroups = {
	"Basic": "",
	"Geek": "",
}

# Only for the platforms you want to use, uncomment the below credentials and fill with your own:
""" # end windog config # """
