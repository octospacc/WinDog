# WinDog

WinDog/WinDogBot is a chatbot I've been (lazily) developing for years, with some special characteristics:

* multi-purpose: it's created for doing a myriad of different things, from the funny to the useful.
* multi-platform: it's an experiment in automagical multiplatform compatibility, with modules targeting a common abstracted API.

The officially-hosted instances of this bot are, respectively:

* [@WinDogBot](https://t.me/WinDogBot) on Telegram
* [@WinDog@botsin.space](https://botsin.space/@WinDog) on Mastodon (can also be used from any other Fediverse platform)

In case you want to run your own instance:

1. `git clone --depth 1 https://gitlab.com/octospacc/WinDog && cd ./WinDog` to get the code.
2. `python3 -m pip install -U -r ./requirements.txt` to install dependencies.
3. `cp ./LibWinDog/Config.py ./` and, in the new file, edit essential fields like user credentials, then delete the unmodified fields.
4. `sh ./StartWinDog.sh` to start the bot every time.

