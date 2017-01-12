import string
from six import StringIO

import spotipy
import requests

from telegram.parsemode import ParseMode
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.inlinekeyboardmarkup import (InlineKeyboardMarkup as IKM,
                                           InlineKeyboardButton as IKB)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          CallbackQueryHandler, Filters)

from spotify_bot import ext


class SpotifyBot(object):

    def __init__(self, config):
        self.config = config

        self.telegram_api_key = config['telegram']
        self.control = ext.SpotifyControl()
        self.spotify = spotipy.Spotify()

    @property
    def keyboard(self):
        if not self.control.is_running():
            return [[KeyboardButton('Activate Spotify')]]

        if self.control.player_state() == 'playing':
            play_pause_button = KeyboardButton('Pause')
        else:
            play_pause_button = KeyboardButton('Play')

        return [[play_pause_button],
                [KeyboardButton('Previous'), KeyboardButton('Next')]]

    def send_message(self, bot, update, msg, disable_link_preview=True,
                     reply_markup=None, *args, **kwargs):
        if not reply_markup:
            reply_markup = ReplyKeyboardMarkup(self.keyboard)

        return bot.sendMessage(update.message.chat_id, msg,
                               reply_markup=reply_markup,
                               resize_keyboard=True,
                               parse_mode=ParseMode.MARKDOWN,
                               disable_web_page_preview=disable_link_preview,
                               *args, **kwargs)

    def send_messages(self, bot, update, messages):
        for msg in messages:
            self.send_message(bot, update, msg)

    def send_photo(self, bot, update, photo, **kwargs):
        bot.sendChatAction(update.message.chat_id, action="upload_photo")

        return bot.sendPhoto(update.message.chat_id, photo=photo, **kwargs)

    def send_photo_url(self, bot, update, url):
        resp = requests.get(url)
        return self.send_photo(bot, update, StringIO(resp.content))

    def command_start(self, bot, update):
        msg = "Hi! I'm a bot to control @MylesB's Spotify account."

        self.send_message(bot, update, msg)

    def command_help(self, bot, update):
        messages = [
            '/status - Get current status of the Spotify application.',
            '/playpause - Toggle play/pause.'
        ]

        self.send_messages(bot, update, messages)

    def command_status(self, bot, update):
        if not self.control.is_running():
            return self.send_message(bot, update, 'Spotify is not running.')

        player_state = self.control.player_state()
        current_track = self.control.current_track()

        if player_state == 'stopped':
            return self.send_message(bot, update, 'Spotify is stopped.')

        msg_line_one = 'Spotify is {0}\n'.format(player_state)
        msg_line_two = '*{name}* by {artist} from ' \
                       '{album}.'.format(**current_track)

        self.send_message(bot, update, msg_line_one + msg_line_two)

    def command_playpause(self, bot, update):
        self.control.playpause()
        self.command_status(bot, update)

    def command_search(self, bot, update, args):
        results = self.spotify.search(q=' '.join(args))

        for r in results['tracks']['items']:
            btn_text = 'Play *{0}* by {1}'.format(r['name'],
                                                  r['artists'][0]['name'])
            button = IKB(text=btn_text,
                         callback_data='play {uri}'.format(**r))

            reply_markup = IKM([[button]])
            self.send_message(bot, update, msg=None,
                              reply_markup=reply_markup)

    def command_play(self, bot, update, args):
        self.control.play_track(''.join(args))
        self.command_status(bot, update)

    def noncommand_text(self, bot, update):
        # Get the message text and convert to lowercase
        text = update.message.text.lower()

        # Remove the punctutation
        punctuation = set(string.punctuation)
        text = ''.join(c for c in text if c not in punctuation)

        if text in ['activate spotify']:
            self.control.activate()
            self.command_status(bot, update)

        if text in ['play', '▶️']:
            self.control.play()
            self.command_status(bot, update)

        if text in ['pause', '⏸']:
            self.control.pause()
            self.command_status(bot, update)

        if text in ['next', '⏭']:
            self.control.next_track()
            self.command_status(bot, update)

        if text in ['previous', '⏮']:
            self.control.previous_track()
            self.command_status(bot, update)

        if text in ['⏯']:
            self.command_playpause(bot, update)

        if text in ['🎉']:
            self.command_play(bot, update,
                              'spotify:track:7LyIoUsiMtelB1I0I4drEF')

        if text in ['🐍']:
            self.command_play(bot, update,
                              'spotify:track:0oIvPKyNldMnehctuxeFH5')

        if text in ['👑']:
            self.command_play(bot, update,
                              'spotify:track:25gSVIBOWeUqXG8DnzpCCs')

    def button(self, bot, update):
        query = str(update.callback_query.message)

        if query.startswith('play '):
            self.command_play(bot, update, query.split('play ')[0])

    def run(self):
        updater = Updater(self.telegram_api_key)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler('start', self.command_start))
        dp.add_handler(CommandHandler('help', self.command_help))

        dp.add_handler(CommandHandler('status', self.command_status))
        dp.add_handler(CommandHandler('playpause', self.command_playpause))
        dp.add_handler(CommandHandler('search', self.command_search,
                                      pass_args=True))
        dp.add_handler(CommandHandler('play', self.command_play,
                                      pass_args=True))

        dp.add_handler(CallbackQueryHandler(self.button))

        dp.add_handler(MessageHandler([Filters.text], self.noncommand_text))

        updater.start_polling()
        updater.idle()
