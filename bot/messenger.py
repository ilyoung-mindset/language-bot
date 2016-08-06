import logging
import random
from datetime import datetime, timedelta
try:
    from urllib import quote
except:
    from urllib.parse import quote

logger = logging.getLogger(__name__)


class Messenger(object):
    def __init__(self, slack_clients):
        self.clients = slack_clients
        self.last_time = {}

    def send_message(self, channel_id, msg):
        # in the case of Group and Private channels, RTM channel payload is a complex dictionary
        if isinstance(channel_id, dict):
            channel_id = channel_id['id']
        logger.debug('Sending msg: {} to channel: {}'.format(msg, channel_id))
        channel = self.clients.rtm.server.channels.find(channel_id)
        channel.send_message("{}".format(msg.encode('ascii', 'ignore')))

    def write_translate(self, channel_id, user_id, text):
        translate_url = "https://translate.google.com/#ro/en/" + quote(text)
        prompts = [
            "_That\'s a good one! How about you try it <{}|in English?>_",
            "_Let's see what <{}|Google Translate> has to say about that_",
            "_Did you mean to say it <{}|in English>?_"
        ]
        txt = random.choice(prompts).format(translate_url)

        key = "{}-{}".format(channel_id, user_id)
        if key in self.last_time:
            time = datetime.utcnow() - self.last_time[key]
            if time < timedelta(minutes=1):
                txt = ":rage1:_<https://www.youtube.com/watch?v=a0x6vIAtFcI|" \
                    "English, motherfucker, do you speak it?>_"
        self.last_time[key] = datetime.utcnow()

        self.clients.web.chat.post_message(
            channel_id, txt, as_user=True, unfurl_links=False,
            unfurl_media=True)

    def write_help_message(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = '{}\n{}\n{}\n{}'.format(
            "I'm your friendly :flag-ro: :oncoming_police_car: bot written in Python.  I'll *_respond_* to the following commands:",
            "> `some text in :flag-ro:` - I'll teach you some English",
            "> `hi <@" + bot_uid + ">` - I'll respond with a randomized greeting mentioning your user. :wave:",
            "> `<@" + bot_uid + "> joke` - I'll tell you one of my finest jokes, with a typing pause for effect. :laughing:")
        self.send_message(channel_id, txt)

    def write_greeting(self, channel_id, user_id):
        greetings = ['Hi', 'Hello', 'Nice to meet you', 'Howdy', 'Salutations']
        txt = '{}, <@{}>!'.format(random.choice(greetings), user_id)
        self.send_message(channel_id, txt)

    def write_prompt(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = "I'm sorry, I didn't quite understand... Can I help you? (e.g. `<@" + bot_uid + "> help`)"
        self.send_message(channel_id, txt)

    def write_joke(self, channel_id):
        question = "Why did the python cross the road?"
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        answer = "To eat the chicken on the other side! :laughing:"
        self.send_message(channel_id, answer)


    def write_error(self, channel_id, err_msg):
        txt = ":face_with_head_bandage: my maker didn't handle this error very well:\n>```{}```".format(err_msg)
        self.send_message(channel_id, txt)
