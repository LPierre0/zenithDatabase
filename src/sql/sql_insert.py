import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from utils import *  

if not os.path.exists("json/dict_stat_id.json"):
    save_dict_to_json({}, "json/dict_stat_id.json")

dict_stat_id = get_json("json/dict_stat_id.json")
actual_id_stat = 1
actual_id_recipe = 1

def add_item(url, rarity, img, name, lvl, item_type, conn, cursor):
    print(f"Inserting items {url}")
    try:
        cursor.execute('''
            INSERT INTO items (url, rarity, img, name, lvl, type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (url, rarity, img, name, lvl, item_type))

        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e} with the item {url}")

def insert_stat(stat, quantity, cursor):
    try:
        cursor.execute('''
            INSERT INTO stat (quantity, type)
            VALUES (?, ?)
        ''', (quantity, stat))

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        

def insert_item_stat(id_item, id_stat, cursor):
    try:
        cursor.execute('''
            INSERT INTO stats_item (url_item, id_stat)
            VALUES (?, ?)
        ''', (id_item, id_stat))

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")




def add_stats_item(url, stats, conn, cursor):
    global dict_stat_id
    global actual_id_stat
    if stats == "No stats":
        return
    for stat in stats:
        quantity = stats[stat]
        key_quantity = str(quantity)
        if stat not in dict_stat_id:
            dict_stat_id[stat] = {}
        if key_quantity not in dict_stat_id[stat]:
            insert_stat(stat, quantity, cursor)
            dict_stat_id[stat][key_quantity] = actual_id_stat
            actual_id_stat += 1
        id_stat = dict_stat_id[stat][key_quantity]
        insert_item_stat(url, id_stat, cursor)
    
    conn.commit()
    
def insert_object_recipe_item(url, url_object, cursor, quantity):
    try:
        cursor.execute('''
                          insert or ignore into object_wakfu (url_object) values (?)
                            ''', (url_object,))
        
        
        cursor.execute('''
            INSERT INTO recipe_with_object (url_object, url_item_recipe, quantity)
            VALUES (?, ?, ?)
        ''', (url_object, url, quantity))


    except sqlite3.Error as e:
        print(f"An error occurred: {e}")  

def insert_item_recipe_item(url, url_item, cursor, quantity):
    try:
        cursor.execute('''
            INSERT INTO recipe_with_item (url_item_recipe, url_item_used, quantity)
            VALUES (?, ?, ?)
        ''', (url, url_item, quantity))



    except sqlite3.Error as e:
        print(f"An error occurred: {e}")  

def add_recipe_item(url, recipe, conn, cursor):
    global actual_id_recipe
    if recipe == "No recipe":
        cursor.execute('''UPDATE items SET have_recipe = ? WHERE url = ?''', (False, url))
    else: 
        cursor.execute('''UPDATE items SET have_recipe = ? WHERE url = ?''', (True, url))
        for url_object in recipe:
            quantity = recipe[url_object]
            if "/armures/" in url_object:
                insert_item_recipe_item(url, url_object, cursor, quantity)
            else:
                if "encyclopedie//" in url_object:
                    url_object = url_object.replace("encyclopedie//", "encyclopedie/ressources/")
                insert_object_recipe_item(url, url_object, cursor, quantity)

def insert_drop_item(url, url_drop, rate, cursor):
    try:
        cursor.execute('''
            INSERT INTO item_drop (url_item, url_mob, rate)
            VALUES (?, ?, ?)
        ''', (url, url_drop, rate))

        cursor.execute('''
                       insert  or ignore into mobs (url_mob) values (?)
                          ''', (url_drop,)) 

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def add_drop_item(url, drop, conn, cursor):

    if drop == "No drop":
        cursor.execute('''UPDATE items SET is_dropable = ? WHERE url = ?''', (False, url))
    else:
        cursor.execute('''UPDATE items SET is_dropable = ? WHERE url = ?''', (True, url))
        for url_drop in drop:
            rate = drop[url_drop]
            insert_drop_item(url, url_drop, rate, cursor)

            


def add_all_json_items(json_file, item_type, conn, cursor):
    items = get_json(json_file)
    for link in items:
        item = items[link]
        add_item(link, item['rarity'], item['img'], item['name'], item['lvl'], item_type, conn, cursor)
        add_stats_item(link, item['stats'], conn, cursor)
        add_recipe_item(link, item['recipe'], conn, cursor)
        add_drop_item(link, item['drop'], conn, cursor)
        conn.commit()
        

def add_all_items_json():
    conn = sqlite3.connect('db/zenith_test.sqlite')
    cursor = conn.cursor()

    list_type = ['Amulette', 'Anneau', 'Armes 1 Main', 'Armes 2 Mains', 'Bottes', 'Bouclier', 'Cape', 'Casque', 'Ceinture', 'Dague', 'Epaulettes', 'Plastron']
    for type_item in list_type:
        add_all_json_items(f'jsonSecure/{type_item}.json', type_item, conn, cursor)
        sleep(1)
        save_dict_to_json(dict_stat_id, "json/dict_stat_id.json")

    conn.close()

def add_build_dictionnary(build_dict):
    conn = sqlite3.connect('db/zenith_test.sqlite')
    cursor = conn.cursor()
    nb_builds_total = len(build_dict)
    nb_builds_inserted = 0
    for link in build_dict:
        build = build_dict[link]
        items = build['items']
        print(items)
        try:
            cursor.execute('''
                INSERT INTO build (url, lvl, name, creation_date, classe, casque_url, amulette_url, plastron_url, anneau1_url, anneau2_url, bottes_url, cape_url, epaulettes_url, ceinture_url, dague_or_bouclier_or_armes_url, armes_url, embleme_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (link, build['lvl'], build['name'], build['date'], build['classe'], items['Casque'], items['Amulette'], items['Plastron'], items['Anneau1'], items['Anneau2'], items['Bottes'], items['Cape'], items['Epaulettes'], items['Ceinture'], items['DagueOrBouclierOrArmes'], items['Armes'], items['Embleme']))

            conn.commit()
            nb_builds_inserted += 1
            print(f"Build {link} inserted. {nb_builds_inserted} builds inserted out of {nb_builds_total}")

        except sqlite3.Error as e:
            print(f"An error occurred: {e} with the build {link}")
            continue
    conn.close()
    return


if __name__ == "__main__":
    add_build_dictionnary(get_json("json/builds.json"))