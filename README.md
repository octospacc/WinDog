# WinDog

WinDog/WinDogBot is a chatbot I've been (lazily) developing for years, with some special characteristics:

* multi-purpose: it's created for doing a myriad of different things, from the funny to the useful (moderation features will be implemented in the future).
* multi-platform: it's an experiment in automagical multiplatform compatibility, with modules targeting a common abstracted API.
* modular: in all of this, the bot is modular, and allows features to be easily activated or removed at will (like some other ones).

The officially-hosted instances of this bot are, respectively:

* [@WinDogBot](https://t.me/WinDogBot) on Telegram
* [@WinDog@botsin.space](https://botsin.space/@WinDog) on Mastodon (can also be used from any other Fediverse platform)

In case you want to run your own instance:

1. `git clone --depth 1 https://gitlab.com/octospacc/WinDog && cd ./WinDog` to get the code.
2. `find -type f -name requirements.txt -exec python3 -m pip install -U -r {} \;` to install the full package of dependencies.
3. `sh ./StartWinDog.sh` to start the bot every time.
    * The first time it runs, it will generate a `Config.py` file, where you should edit essential fields (like user credentials), uncommenting them where needed, then delete the unmodified fields. Restart the program to load the updated configuration.

All my source code mirrors for the bot:

* GitLab (primary): <https://gitlab.com/octospacc/WinDog>
* GitHub: <https://github.com/octospacc/WinDog>
* Gitea.it: <https://gitea.it/octospacc/WinDog>

