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

def add_all_json():
    conn = sqlite3.connect('db/zenithDatabase.sqlite')
    cursor = conn.cursor()

    list_type = ['Amulette', 'Anneau', 'Armes 1 Main', 'Armes 2 Mains', 'Bottes', 'Bouclier', 'Cape', 'Casque', 'Ceinture', 'Dague', 'Emblème', 'Epaulettes', 'Plastron']
    for type in list_type:
        add_all_json_items(f'json/{type}.json', type, conn, cursor)

    conn.close()

if __name__ == '__main__':
    add_all_json()