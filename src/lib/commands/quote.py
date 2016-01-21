import globals
from src.lib.queries.quotes_queries import *


def quote():
    q = Quotes()
    channel = globals.global_channel
    # (1, u'testchannel', u'testuser', u'quote', 1, u'testgame')
    quote_data = q.get_quote(channel)
    if quote_data is None:
        return "No quotes found. Why not add one with '!addquote [quote]'?"
    else:
        quote = str(quote_data[3])
        quote_number = quote_data[4]
        game = quote_data[5]
        resp = "Quote #{0}: \"{1}\" [{2}]".format(quote_number, quote, game)
        return resp
