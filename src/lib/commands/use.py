import globals
from src.lib.queries.pokemon_queries import *


def use(args):
    item = args[0]
    position = args[1]

    return use_item(globals.CURRENT_USER, item, position)
