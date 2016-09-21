[![Code Climate](https://codeclimate.com/github/myles/telegram-myles-bot/badges/gpa.svg)](https://codeclimate.com/github/myles/telegram-spotify-bot)

# Myles' Spotify Bot

A Telegram Bot I created to control my Spotify account.

## Requirments

* [Telegram Bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot)

## Development Environment Setup

You will need the following:

* Python 2.5
* pip
* virtualenvwrapper
* API Keys for Spotify

Start by cloning the repository:

```
$ git clone git@github.com:myles/telegram-spotify-bot
$ cd ~/telegram-spotify-bot
```

Create a Python virtual environment:

```
~/telegram-spotify-bot $ mkvritualenv telegram-spotify-bot
(telegram-spotify-bot) ~/telegram-spotify-botbot $
```

The (telegram-spotify-bot) prefix indicates that a virtual environment called
"telegram-spotify-bot" is being used. Next, check that you have the correct
version of Python:

```
(telegram-spotify-bot) ~/telegram-spotify-bot $ python --version
Python 3.5.2
(telegram-spotify-bot) ~/telegram-spotify-bot $ pip 8.0.2 from /Users/Myles/.virtualenvs/telegram-spotify-bot/lib/python3.5/site-packages (python 3.5)
```

Install the project requirements:

```
(telegram-spotify-bot) ~/telegram-spotify-bot $ pip install -U -r requirements.txt
```

Create the configuration file at `config.json` that looks like:

```
{
  "telegram": "TELEGRAM_API_KEY"
}
```

