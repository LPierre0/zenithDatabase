from scraping_build import * 

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


if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    routine()