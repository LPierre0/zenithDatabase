import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from utils import *  



def add_item(url, rarity, img, name, lvl, item_type, conn, cursor):
    try:
        cursor.execute('''
            INSERT INTO item (url, rarity, img, name, lvl, type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (url, rarity, img, name, lvl, item_type))

        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")



def add_all_json_items(json_file, item_type, conn, cursor):
    items = get_json(json_file)
    for link in items:
        item = items[link]
        add_item(link, item[2], item[3], item[1], item[0], item_type, conn, cursor)

def add_all__items_json():
    conn = sqlite3.connect('db/zenithDatabase.sqlite')
    cursor = conn.cursor()

    list_type = ['Amulette', 'Anneau', 'Armes 1 Main', 'Armes 2 Mains', 'Bottes', 'Bouclier', 'Cape', 'Casque', 'Ceinture', 'Dague', 'Emblème', 'Epaulettes', 'Plastron']
    for type in list_type:
        add_all_json_items(f'json/{type}.json', type, conn, cursor)

    conn.close()

def add_build_dictionnary(build_dict):
    conn = sqlite3.connect('db/zenithDatabase.sqlite')
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
            break
    conn.close()
    return


if __name__ == "__main__":
    add_build_dictionnary(get_json('json/builds.json'))