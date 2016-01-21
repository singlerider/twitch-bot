import globals
from src.lib.queries.pokemon_queries import *

usage = "!party [position/'members']"


def cron(a=None):
    return "New to the channel? Use '!catch', then '!battle' one of my party members: " + \
        str(get_user_party_info("lorenzotherobot"))


def party(args):
    position = args[0]
    if position in ['1', '2', '3', '4', '5', '6']:
        nickname, pokemon_type1_id, pokemon_type2_id, pokemon_name, pokemon_type1, pokemon_type2 = user_pokemon_types_summary(
            globals.CURRENT_USER, position)
        level, nickname, hp, speed, attack, defense, special_attack, special_defense = get_battle_stats(
            globals.CURRENT_USER, position)
        return "lvl " + str(level) + " " + pokemon_name.decode("utf8") + ": HP " + str(hp) + ", Att " + str(attack) + ", Spd " + str(speed) + \
            ", Def " + str(defense) + ", SpAtt " + str(special_attack) + ", SpDef " + \
            str(special_defense) + ", " + pokemon_type1 + ", " + pokemon_type2
    elif args[0] == 'members':
        party_members = get_user_party_info(globals.CURRENT_USER)
        return party_members
    else:
        try:
            party = get_user_party_info(position)
            if len(party) > 0:
                print len(party)
                return party
            else:
                print party
                return "User not found. Check your spelling"
        except Exception as err:
            print Exception, err
            return "Usage: " + usage
