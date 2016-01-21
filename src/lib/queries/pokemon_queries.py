#!/usr/bin/python
# -*- coding: utf-8 -*-

from src.lib.queries.connection import *
from src.lib.queries.points_queries import *


def get_pokemon_id_from_name(pokemon_name):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT pokemon.id FROM pokemon WHERE pokemon.name = %s""", [
                pokemon_name])
        pokemon_id = cur.fetchone()
        cur.close()
        if int(pokemon_id[0]) != 0:
            return pokemon_id[0]
        else:
            return "Error"


def find_open_party_positions(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT position FROM userpokemon WHERE username = %s
                ORDER BY position""", [username])
        occupied_positions = cur.fetchall()
        simple_list = [x[0] for x in occupied_positions]
        possible_positions = [1, 2, 3, 4, 5, 6]
        available_positions = list(set(possible_positions) - set(simple_list))
        cur.close()
        return available_positions, occupied_positions


def insert_user_pokemon(
        username, caught_by, position, id, level,
        nickname, for_trade, for_sale):
    con = get_connection()
    try:
        with con:

            cur = con.cursor()
            cur.execute("""INSERT INTO userpokemon (username, caught_by,
                position, pokemon_id, level, nickname, for_trade, for_sale)
                VALUES (%s, %s, %s, %s, %s, (
                        SELECT name FROM pokemon WHERE id = %s), 0, 0)""", [
                        username, caught_by, position, id, level, id])
            cur.execute("""SELECT nickname FROM userpokemon
                WHERE username = %s AND position = %s""", [
                        username, position])
            pokemon_caught = cur.fetchone()
            cur.close()
            return str(pokemon_caught[0]) + ' was caught!'
    except:
        return "Party full. One empty slot in party needed."


def remove_user_pokemon(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        success = cur.execute(
            """DELETE FROM userpokemon WHERE username = %s
                AND position = %s""", [username, position])
        cur.close()
        if (success):
            return "Released party member #" + str(position)
        else:
            return "Nothing to release!"


def get_user_party_info(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.position, userpokemon.level,
                userpokemon.nickname
                FROM userpokemon WHERE username = %s
                ORDER BY userpokemon.position""", [username])
        party_members = cur.fetchall()
        cur.close()
        if party_members is not None:
            party_member_comprehension = ["({}) lvl {}, {}".format(
                x, y, z) for x, y, z in party_members]
            return " | ".join(party_member_comprehension)
        else:
            return "No Pokemon found. Tell them to use !catch"


def get_user_battle_info(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.position, userpokemon.level
                FROM userpokemon WHERE username = %s
                ORDER BY userpokemon.position""", [username])
        party_members = cur.fetchall()
        cur.close()
        return party_members


def user_pokemon_types_summary(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""SELECT userpokemon.nickname AS 'Nickname',
        type_primary.id as 'ID 1', type_secondary.id AS 'ID 2',
        pokemon.name AS 'Name', type_primary.identifier AS 'Type 1',
        type_secondary.identifier AS 'Type 2'
        FROM userpokemon INNER JOIN pokemon
            ON pokemon.id = userpokemon.pokemon_id inner
        JOIN types AS type_primary
            ON (type_primary.id = pokemon.type_primary)
        LEFT OUTER JOIN types AS type_secondary
            ON (type_secondary.id = pokemon.type_secondary)
        WHERE username = %s AND userpokemon.position = %s""", [
            username, position])
        types_summary = cur.fetchone()
        nickname = types_summary[0]
        pokemon_type1_id = types_summary[1]
        pokemon_type2_id = types_summary[2]
        pokemon_name = types_summary[3]
        pokemon_type1 = types_summary[4]
        cur.close()
        if types_summary[2] and types_summary[5] is not None:
            pokemon_type2 = types_summary[5]
            return nickname, pokemon_type1_id, pokemon_type2_id, pokemon_name, pokemon_type1, pokemon_type2
        else:
            pokemon_type2 = "No secondary type."
            return nickname, pokemon_type1_id, 'none', pokemon_name, pokemon_type1, 'none'


def level_up_user_pokemon(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""update userpokemon set level = level + 1
        where username = %s and position = %s
        """, [username, position])
        cur.close()


def get_last_battle(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT lastbattle from users WHERE username = %s""", [username])
        last_battle = cur.fetchone()
        cur.close()
        return last_battle[0]


def set_battle_timestamp(username, datetime):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """UPDATE users SET lastbattle = %s WHERE username = %s""", [
                datetime, username])
        cur.close()


def get_battle_stats(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
        SELECT username,
            userpokemon.nickname AS 'Nickname',
            userpokemon.level AS 'Level',
            pokemon.name AS 'Name',
            type_primary AS 'Type 1',
            type_secondary AS 'Type 2',
            ((2*pokemon.hp_base)/100*userpokemon.level)+110
                AS 'Health Points',
            ((2*pokemon.speed_base)/100*userpokemon.level)+5
                AS 'Speed',
            ((2*pokemon.attack_base)/100*userpokemon.level)+5
                AS 'Attack',
            ((2*pokemon.defense_base)/100*userpokemon.level)+5
                AS 'Defense',
            ((2*pokemon.special_attack_base)/100*userpokemon.level)+5
                AS 'Special',
            ((2*pokemon.special_defense_base)/100*userpokemon.level)+5
                AS 'Special Defense'
            FROM userpokemon
            INNER JOIN pokemon ON pokemon.id = userpokemon.pokemon_id
            WHERE username = %s AND userpokemon.position = %s
        """, [username, position])
        battle_stats = cur.fetchone()
        # print battle_stats
        nickname = battle_stats[1]
        level = battle_stats[2]
        hp = int(round(battle_stats[6]))
        speed = int(round(battle_stats[7]))
        attack = int(round(battle_stats[8]))
        defense = int(round(battle_stats[9]))
        special_attack = int(round(battle_stats[10]))
        special_defense = int(round(battle_stats[11]))
        cur.close()
        return level, nickname, hp, speed, attack, defense, special_attack, special_defense


def get_attacker_multiplier(attacker_type, defender_type):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""SELECT * from types WHERE id = %s""", [attacker_type])
        attacker_multipliers = cur.fetchone()
        row_correction = defender_type + 1
        attacker_effect = attacker_multipliers[row_correction]
        cur.close()
        return attacker_effect


def get_defender_multiplier(attacker_type, defender_type):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""SELECT * from types WHERE id = %s""", [defender_type])
        defender_multipliers = cur.fetchone()
        row_correction = attacker_type + 1
        defender_effect = defender_multipliers[row_correction]
        cur.close()
        return defender_effect

is_tradeable = 1
asking_pokemon_id = 150
minimum_level = 10
party_position = 1


def get_pokemon_id(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.pokemon_id WHERE username = %s and position = %s
        """, [username, position])
        pokemon_id = cur.fetchone()
        cur.close()
        return pokemon_id


def reset_trade_timestamp(time):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE userpokemon SET for_trade = 0, time_trade_set = NULL
                WHERE time_trade_set < %s
            """, [time])
        cur.close()


def set_pokemon_trade_status(
        time, asking_pokemon_id, minimum_level, username, party_position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE userpokemon SET time_trade_set = %s, for_trade = 1,
                    asking_trade = %s, asking_level = %s
                WHERE username = %s AND position = %s
        """, [
            time, asking_pokemon_id, minimum_level, username, party_position])
        cur.close()


def get_receiver_trade_status(position, receiver):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT pokemon_id, level FROM userpokemon
                WHERE username = %s AND position = %s
        """, [receiver, position])
        trader_party = cur.fetchall()
        cur.close()
        return trader_party


def get_giver_trade_status(position, giver):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT asking_trade, asking_level FROM userpokemon
                WHERE username = %s AND position = %s
        """, [giver, position])
        trader_party = cur.fetchall()
        cur.close()
        return trader_party


def show_all_tradable_pokemon():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT
                userpokemon.username,
                owner_pokemon.name,
                userpokemon.position,
                asking_for.name,
                asking_level
                FROM userpokemon
                INNER JOIN pokemon AS owner_pokemon
                    ON owner_pokemon.id = userpokemon.pokemon_id
                LEFT OUTER JOIN pokemon AS asking_for
                    ON asking_for.id = userpokemon.asking_trade
                WHERE for_trade = 1
        """)
        trades = cur.fetchall()
        cur.close()
        return trades


def show_user_tradable_pokemon(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT
                userpokemon.username,
                owner_pokemon.name,
                userpokemon.position,
                asking_for.name,
                asking_level
                FROM userpokemon
                INNER JOIN pokemon AS owner_pokemon
                    ON owner_pokemon.id = userpokemon.pokemon_id
                LEFT OUTER JOIN pokemon AS asking_for
                    ON asking_for.id = userpokemon.asking_trade
                WHERE for_trade = 1 AND username = %s
        """, [username])
        trades = cur.fetchall()
        cur.close()
        return trades


def add_win(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE users SET wins = wins + 1 WHERE username = %s
        """, [username])
        cur.close()


def add_loss(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE users SET losses = losses + 1 WHERE username = %s
        """, [username])
        cur.close()


def trade_transaction(giver, giver_position, receiver, receiver_position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE userpokemon SET username = %s, for_trade = 2, position = 0
                WHERE username = %s
                    AND position = %s""", [receiver, giver, giver_position])
        cur.execute("""
            UPDATE userpokemon SET username = %s, for_trade = 2, position = %s
                WHERE username = %s
                    AND position = %s""", [
            giver, giver_position, receiver, receiver_position])
        cur.execute("""
            UPDATE userpokemon SET position = %s, for_trade = 2
                WHERE position = 0""", [receiver_position])
        cur.execute("""
            UPDATE userpokemon SET time_trade_set = NULL
                WHERE username = %s AND position = %s
        """, [receiver, receiver_position])
        cur.close()


def show_all_pokemon_for_sale():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.username
                    AS 'Owner', pokemon.name, userpokemon.asking_price
                FROM userpokemon
                INNER JOIN pokemon ON pokemon.id = userpokemon.pokemon_id
                WHERE for_sale = 1;""")
        cur.close()


def show_user_pokemon_for_sale():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.username, pokemon.name, userpokemon.position
                FROM userpokemon
                INNER JOIN pokemon ON pokemon.id = userpokemon.pokemon_id
                WHERE for_sale = 1 AND username = %s""", [
                    globals.CURRENT_USER])
        cur.close()


def check_for_pokemon_for_sale():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.username, pokemon.name, userpokemon.asking_price
                FROM pokemon
                LEFT JOIN userpokemon on userpokemon.pokemon_id = pokemon.id
                WHERE for_sale = 1 and pokemon.name = %s""", [pokemon_query])
        cur.close()


def set_pokemon_as_for_sale():
    con = get_connection()
    for_sale = 1
    asking_price = 5000
    with con:
        cur = con.cursor()
        cur.execute("""
        UPDATE userpokemon
        SET for_sale = %s, asking_price = %s
        WHERE username = %s AND position = %s""", [
            for_sale, asking_price, globals.CURRENT_USER, party_position])
        cur.close()


def update_asking_price():
    con = get_connection()
    asking_price = 4000
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE userpokemon SET asking_price = %s
                WHERE username = %s AND position = %s""", [
                    asking_price, globals.CURRENT_USER, party_position])
        cur.close()


def sell_transaction():
    con = get_connection()
    seller = 'lorenzotherobot'
    buyer = globals.CURRENT_USER
    open_position = 5
    with con:
        cur = con.cursor()
        cur.execute("""SET @seller = %s""", [seller])
        cur.execute("""@position = %s""", [party_position])
        cur.execute("""SET @buyer = %s""", [buyer])
        cur.execute("""SET @position_free = %s""", [open_position])
        cur.execute("""
            SET @price = (
                SELECT asking_price FROM userpokemon WHERE username = @owner
                    AND position = @position)""")
        cur.execute("""
            UPDATE userpokemon SET username = @buyer, for_sale = 0,
                position = @position_free WHERE username = @seller
                    AND position = @position""")
        cur.execute("""
            UPDATE users SET donation_points = donation_points + @price
                WHERE username = @seller""")
        cur.execute("""
            UPDATE users SET donation_points = donation_points - @price
                WHERE username = @buyer""")
        cur.execute("""COMMIT""")
        cur.close()


def spawn_tallgrass(rarity_index):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT name FROM pokemon WHERE rarity = %s
                AND evolution_trigger = 0 AND id != 244
                AND id != 251 ORDER BY rand() limit 1""", [
                    rarity_index])  # Intentionally excludes Entei
        rare_pokemon = cur.fetchone()
        cur.close()
        return rare_pokemon[0]


def check_evolution_eligibility(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT userpokemon.nickname, pokemon.name, pokeset.name, pokeset.id
                FROM userpokemon
                JOIN pokemon ON userpokemon.pokemon_id = pokemon.id
                JOIN pokemon AS pokeset
                    ON pokemon.evolution_set = pokeset.evolution_set
                WHERE userpokemon.level >= pokemon.evolution_level
                    AND pokeset.id > userpokemon.pokemon_id
                    AND userpokemon.username = %s
                    AND userpokemon.position = %s LIMIT 1
            """, [username, position])
        eligible_evolution = cur.fetchone()
        cur.close()
        return eligible_evolution

        # | nickname  | name      | name    | id |
        # | Bulbasaur | Bulbasaur | Ivysaur |  2 |


def check_trade_evolution_eligibility(username, position):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""SELECT userpokemon.nickname, pokemon.name, pokeset.name, pokeset.id,
        pokeset.evolution_set, pokeset.evolution_index, pokeset.evolution_trigger, userpokemon.for_trade
        FROM userpokemon JOIN pokemon on userpokemon.pokemon_id = pokemon.id
        JOIN pokemon as pokeset on pokemon.evolution_set = pokeset.evolution_set
        WHERE userpokemon.username = %s AND userpokemon.position = %s
        AND pokeset.evolution_index = pokemon.evolution_index + 1
        AND pokeset.evolution_trigger = 20 and for_trade = 2;
        """, [username, position])

        # +----------+---------+--------+----+---------------+-----------------+-------------------+
        # | nickname | name    | name   | id | evolution_set | evolution_index + evolution_trigger |
        # +----------+---------+--------+----+---------------+-----------------+-------------------+
        # | Haunter  | Haunter | Gengar | 94 |            39 |               3 +                20 |
        # +----------+---------+--------+----+---------------+-----------------+-------------------+

        eligible_evolution = cur.fetchone()
        cur.close()
        return eligible_evolution


def apply_evolution(username, position):
    con = get_connection()
    evolution_result = check_evolution_eligibility(username, position)
    trade_evolution_result = check_trade_evolution_eligibility(
        username, position)
    if evolution_result is not None:
        nickname = evolution_result[0]
        id = evolution_result[3]
        if nickname == evolution_result[1]:
            nickname = evolution_result[2]
        with con:
            cur = con.cursor()
            cur.execute("""
                UPDATE userpokemon SET pokemon_id = %s, nickname = %s
                    WHERE username = %s AND position = %s
                """, [id, nickname, username, position])
            cur.close()
            return nickname + " has evolved! Raise your Kappa s!!!"
    elif trade_evolution_result is not None:
        con = get_connection()
        nickname = trade_evolution_result[0]
        id = trade_evolution_result[3]
        if nickname == trade_evolution_result[1]:
            nickname = trade_evolution_result[2]
        with con:
            cur = con.cursor()
            cur.execute("""
                UPDATE userpokemon SET pokemon_id = %s, nickname = %s
                    WHERE username = %s AND position = %s
                """, [id, nickname, username, position])
            cur.close()
            return nickname + " has evolved! Raise your Kappa s!!!"
    else:
        return "No Pokemon eligible for evolution."


def update_nickname(nickname, username, position):
    con = get_connection()
    # TODO - error message on no entry
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE userpokemon SET nickname = %s WHERE username = %s
                AND position = %s""", [nickname, username, position])
        cur.close()


def check_items():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT id, name, value FROM items WHERE id IN (1,2,3,4,5,11)
            """)
        for_sale = cur.fetchall()
        cur.close()
        return for_sale


def get_item_value(id):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""SELECT value FROM items WHERE id = %s""", [id])
        value = cur.fetchone()
        cur.close()
        return value[0]


def check_inventory(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT items.id, items.name, useritems.quantity
                FROM useritems
                INNER JOIN items ON items.id = useritems.item_id
                WHERE username = %s
            """, [username])
        inventory = cur.fetchall()
        cur.close()
        return inventory


def buy_items(id, username):
    con = get_connection()
    with con:
        try:
            if int(id) in (1, 2, 3, 4, 5, 11):
                points = int(get_user_points(username))
                value = int(get_item_value(id))
                if points >= value:
                    cur = con.cursor()
                    cur.execute("""
                        INSERT INTO useritems (username, item_id, quantity)
                                VALUES (%s, %s, 1) ON DUPLICATE KEY
                                UPDATE quantity = quantity + 1""", [
                        username, id])
                    cur.execute("""
                        UPDATE users SET donation_points = donation_points - %s
                            WHERE username = %s""", [value, username])
                    cur.close()
                    return "Transaction successful."
                else:
                    return "You need more points for that!"
            else:
                return "That is not a valid item position."
        except Exception as error:
            print error
            return "item ID must be a number"


def gift_items(id, username):
    con = get_connection()
    try:
        if int(id) in (1, 2, 3, 4, 5, 11):
            with con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO useritems (username, item_id, quantity)
                            VALUES (%s, %s, 1) ON DUPLICATE KEY
                        UPDATE quantity = quantity + 1""", [username, id])
                cur.close()
                return "Gift successful."
        else:
            return "That is not a valid item position."
    except Exception as error:
        print error
        return "Item ID must be a number"


def use_item(username, item, position):
    con = get_connection()
    try:
        item = int(item)
        item_in_stock = False
        inventory = check_inventory(username)
        for id, __, __ in inventory:
            if int(id) == int(item):
                item_in_stock = True
        if item == 11 and item_in_stock:
            with con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE userpokemon SET level = level + 10
                        WHERE username = %s AND position = %s
                    """, [username, position])
                cur.execute("""
                    UPDATE userpokemon SET level = 100
                        WHERE username = %s AND position = %s AND level > 100
                    """, [username, position])
                cur.execute("""
                    UPDATE useritems SET quantity = quantity - 1
                        WHERE username = %s AND item_id = %s
                    """, [username, item])
                cur.execute("""
                    DELETE FROM useritems WHERE username = %s
                        AND quantity <= 0""", [username])
                cur.close()
                return "LEVEL UP!!!"
        else:

            def check_special_evolution_eligibility(username, position, item):
                with con:
                    cur = con.cursor()
                    cur.execute("""
                        SELECT userpokemon.nickname, pokemon.name,
                            pokeset.name, pokeset.id, pokeset.evolution_set,
                            pokeset.evolution_index, pokeset.evolution_trigger
                            FROM userpokemon
                            JOIN pokemon ON userpokemon.pokemon_id = pokemon.id
                            JOIN pokemon AS pokeset
                                ON pokemon.evolution_set = pokeset.evolution_set
                            WHERE userpokemon.username = %s
                            AND userpokemon.position = %s
                            AND pokeset.evolution_index = pokemon.evolution_index + 1
                            AND pokeset.evolution_trigger = %s
                        """, [username, position, item])

                    # +----------+-------+----------+-----+---------------+-----------------+-------------------+
                    # | nickname | name  | name     | id  | evolution_set | evolution_index | evolution_trigger |
                    # +----------+-------+----------+-----+---------------+-----------------+-------------------+
                    # | Eevee    | Eevee | Vaporeon | 134 |            51 |               2 |                 2 |
                    # +----------+-------+----------+-----+---------------+-----------------+-------------------+

                    eligible_evolution = cur.fetchone()
                    cur.close()
                    return eligible_evolution
            evolution_result = check_special_evolution_eligibility(
                username, position, item)
            nickname = evolution_result[0]
            id = evolution_result[3]
            if evolution_result is not None:
                if nickname == evolution_result[1]:
                    nickname = evolution_result[2]
                with con:
                    cur = con.cursor()
                    cur.execute("""
                        UPDATE useritems SET quantity = quantity - 1
                            WHERE username = %s AND item_id = %s
                        """, [username, item])
                    cur.execute("""
                        UPDATE userpokemon SET pokemon_id = %s, nickname = %s
                            WHERE username = %s AND position = %s
                        """, [id, nickname, username, position])
                    cur.execute("""
                        DELETE FROM useritems WHERE username = %s
                            AND quantity <= 0""", [username])
                    cur.close()
                    return nickname + " has evolved! Raise your Kappa s!!!"
            else:
                return "No Pokemon eligible for evolution."
    except Exception as error:
        print error
        return "Well, that didn't work. Did you pick the right items? Do you actually have those items? Kappa"


def get_leaderboard():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT username, wins, losses FROM users WHERE wins > 25
                ORDER BY wins/losses * 1 DESC
            """)
        user_data = cur.fetchall()
        user_data_comprehension = ["{}: W{}, L{}, {}%".format(str(x), int(y), int(
            z), int((float(y) / ((float(y) + float(z)))) * 100)) for x, y, z in user_data]
        cur.close()
        return "The top 10 trainers are " + \
            str(" | ".join(user_data_comprehension[0:9]))
