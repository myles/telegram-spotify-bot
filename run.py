import json
import logging

from spotify_bot.bot import SpotifyBot as Bot

logging.basicConfig(filename='bot.log', format='%(asctime)s %(message)s',
                    level=logging.DEBUG)


def main():
    with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())

    bot = Bot(config)
    bot.run()


if __name__ == '__main__':
    main()
