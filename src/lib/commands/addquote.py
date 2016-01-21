import globals
from src.lib.queries.quotes_queries import *
from src.lib.twitch import *


def addquote(args):
    q = Quotes()
    user = globals.CURRENT_USER
    channel = globals.global_channel
    quote = unicode(args[0].strip().strip("\"").strip("\'"), 'utf-8')
    if len(quote) > 300:
        return "Let's keep it below 300 characters?"
    game = get_stream_game(channel)
    q.add_quote(channel, user, quote, game)
    return "{0} added!".format(quote)
