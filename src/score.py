import sqlite3
from utils import *
dict_rarity_points = {
    "common": 0,
    "rare": 1,
    "mythic": 5,
    "legendary": 10,
    "relic": 8,
    "epic" : 8,
    "memory" : 10
}

list_not_here = []

def get_builds(cursor, item_link, type_item):
    if type_item.lower() == "anneau":
        return get_builds(cursor, item_link, "anneau1") + get_builds(cursor, item_link, "anneau2")
    try:
        cursor.execute(f"SELECT amulette_url, anneau1_url, anneau2_url, armes_url, bottes_url, cape_url, casque_url, ceinture_url, dague_or_bouclier_or_armes_url, embleme_url, epaulettes_url, plastron_url FROM build WHERE {type_item.lower()}_url = '{item_link}'")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_mean_score_rarity(cursor, link, type_item, dict_rarity):
    score = 0
    i = 0
    global list_not_here
    for items in get_builds(cursor, link, type_item):
        for item in items:
            if item != link and item is not None:
                print(item)
                if item not in dict_rarity:
                    print(f"Error: {item} not in dict_rarity")
                    if item not in list_not_here:
                        list_not_here.append(item)
                    continue
                if dict_rarity[item] not in dict_rarity_points:
                    print(f"Error: {item} not in dict_rarity_points")
                    continue
                score += dict_rarity_points[dict_rarity[item]]
                i += 1
    if i == 0:
        return 0
    return score / i

                

def get_item_link_rarity(cursor):
    cursor.execute(f"SELECT url, rarity, type FROM items")
    return cursor.fetchall()

def get_score(cursor):
    items_link = get_item_link_rarity(cursor)
    dict_rarity = {}
    for link, rarity, type_item in items_link:
        print(link, rarity, type_item)
        dict_rarity[link] = rarity
    dict_score = {}
    for link, rarity, type_item in items_link:
        score_self_rarity = dict_rarity_points[rarity]
        score_item_with = get_mean_score_rarity(cursor, link, type_item, dict_rarity)
        dict_score[link] = score_self_rarity * score_item_with
    sorted_dict = dict(sorted(dict_score.items(), key=lambda item: item[1], reverse=True))
    save_dict_to_json(sorted_dict, 'score.json')


def get_item_popularity(cursor, link_item, type_item):
    query = f"""
    SELECT items.url, items.rarity, COUNT(*) AS count 
    FROM build 
    JOIN items ON items.url = build.{type_item}_url 
    WHERE items.url = '{link_item}'
    GROUP BY items.url, items.rarity
    """

    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_list(cursor):
    cursor.execute("SELECT url, type, lvl, rarity FROM items")
    data = cursor.fetchall()
    list_item_link = []
    list_type = []
    list_lvl = []
    list_rarity = []
    for item in data:
        list_item_link.append(item[0])
        list_type.append(item[1])
        list_lvl.append(item[2])
        list_rarity.append(item[3])

    return list_item_link, list_type, list_lvl, list_rarity


def get_dict_item(cursor, dict_rarity):
    ## input : cursor
    ## output : dict with key = url and value = score rarity, score popularity, score rarity 
    dict = {}
    list_item_link, list_type, list_lvl, list_rarity = get_list(cursor)
    for item_link, type_item, list_lvl, list_rarity in zip(list_item_link, list_type, list_lvl, list_rarity):
        if type_item.lower() == "anneau":
            type_item = "anneau1"
        popularity = get_item_popularity(cursor, item_link, type_item)
        rarity_around = get_mean_score_rarity(cursor, item_link, type_item, dict_rarity)
        rarity_score = dict_rarity_points[list_rarity]
        dict[item_link] = [rarity_score, popularity, rarity_around]
    return dict

def get_dict_rarity(cursor):
    ## input : cursor
    ## output : dict with key = url and value = rarity
    dict = {}
    cursor.execute("SELECT url, rarity FROM items")
    data = cursor.fetchall()
    for item in data:
        dict[item[0]] = item[1]
    return dict

def normalize(list):
    ## input : list of score
    ## output : list of score normalized
    max_score = max(list)
    min_score = min(list)
    return [(score - min_score) / (max_score - min_score) for score in list]

def get_score(dict):
    ## input : dict with key = url and value = score rarity, score popularity, score rarity around normalized
    ## output : score = score rarity + score popularity + score rarity around weighted
    list_tranche = [(0, 20), (21, 35), (36, 50), (51, 65), (66, 80), (81, 95), (96, 110), (111, 125), (126, 140), (141, 155), (156, 170), (171, 185), (186, 200), (201, 215), (216, 230)]

    for lvl_min, lvl_max in list_tranche:
        list_item_link = []
        list_popularity = []
        list_rarity = []
        list_rarity_around = []
        for item_link in dict:
            if dict[item_link][2] >= lvl_min and dict[item_link][2] <= lvl_max:
                list_item_link.append(item_link)
                list_rarity.append(dict[item_link][0])
                list_popularity.append(dict[item_link][1])
                list_rarity_around.append(dict[item_link][2])

        list_rarity = normalize(list_rarity)
        list_popularity = normalize(list_popularity)
        list_rarity_around = normalize(list_rarity_around)
        for item_link, rarity, popularity, rarity_around in zip(list_item_link, list_rarity, list_popularity, list_rarity_around):
            dict[item_link] = [rarity, popularity, rarity_around]
        
            
    return dict

conn = sqlite3.connect('db/zenith.sqlite')
cursor = conn.cursor()

dict_rarity = get_dict_rarity(cursor)
dict_item = get_dict_item(cursor, dict_rarity)

with open("elem_to_scrap.txt", "w") as f:
    for elem in list_not_here:
        f.write(elem + "\n")

    