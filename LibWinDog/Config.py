# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #
""" # windog config start # """

# If you have modified the bot's code, you should set this.
ModifiedSourceUrl = ""

# Logging of system information and runtime errors. Recommended to be on in some way to diagnose errors.
LogToConsole = True
LogToFile = True

# Dumping of the bot's remote events. Should stay off unless needed for debugging.
DumpToConsole = False
DumpToFile = False

AdminIds = [ "telegram:123456789", "telegram:634314973", "matrix:@admin:matrix.example.com", "matrix:@octt:matrix.org", "activitypub:admin@mastodon.example.com", ]

BridgesConfig: list[tuple[str, str]] = []

DefaultLanguage = "en"
Debug = False
CommandPrefixes = ".!/"
WebUserAgent = "WinDog v.Staging"

FailOnImportError = False

# Only for the platforms you want to use, uncomment the below credentials and fill with your own:
""" # end windog config # """
