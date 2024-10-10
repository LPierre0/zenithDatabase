import argparse
from scraper.build_scraper import Build_Scrapper
from scraper.stats_scraper import Stats_Scraper
from scraper.items_scraper import Items_Scraper


import sqlite3



def reset_sql():
    tables = ['builds', 'items', 'stats', 'stats_item', 'object_wakfu', 'recipe_with_object']
    conn = sqlite3.connect('db/zenith_test.sqlite')
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f'''
            DELETE FROM {table}
        ''')
    conn.commit()
    conn.close()

def reset_json():
    import os
    files = os.listdir('json')
    for file in files:
        os.remove(f'json/{file}')

def reset_all():
    reset_sql()
    reset_json()



def routine():
    get_all_build_from_date(get_yesterday_date())


def rescrap_build():
    get_all_build()

def rescrap_items():
    get_json_items()
    
def rescrap_recipe():
    get_all_items_information()

def rescrap_all():
    rescrap_build()
    rescrap_items()
    rescrap_recipe()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script pour lancer différentes routines.")
    parser.add_argument('--routine', action='store_true', help="Lancer la routine")
    parser.add_argument('--resetSQL', action='store_true', help="Réinitialiser toutes les tables sql")
    parser.add_argument('--resetJSON', action='store_true', help="Réinitialiser les json")
    parser.add_argument('--resetALL', action='store_true', help="Réinitialiser tout")
    parser.add_argument('--rescrapBuild', action='store_true', help="Rescraper les builds")
    parser.add_argument('--rescrapItems', action='store_true', help="Rescraper les items")
    parser.add_argument('--rescrapRecipe', action='store_true', help="Rescraper les recettes")
    parser.add_argument('--rescrapAll', action='store_true', help="Rescraper tout")




    args = parser.parse_args()

    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)

    if args.routine:
        routine()
    elif args.reset:
        reset_all()