import json
import logging
import re
from langdetect import detect

logger = logging.getLogger(__name__)


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself
        user = event.get('user')
        if not user and self.clients.is_message_from_me(user):
            return

        msg_txt = event.get('text', '')
        if len(msg_txt) > 5 and detect(msg_txt) == 'ro':
            self.msg_writer.write_translate(event['channel'], user, msg_txt)
        elif self.clients.is_bot_mention(msg_txt):
            # e.g. user typed: "@pybot tell me a joke!"
            if 'help' in msg_txt:
                self.msg_writer.write_help_message(event['channel'])
            elif re.search('hi|hey|hello|howdy', msg_txt):
                self.msg_writer.write_greeting(event['channel'], event['user'])
            elif 'joke' in msg_txt:
                self.msg_writer.write_joke(event['channel'])
            else:
                self.msg_writer.write_prompt(event['channel'])
