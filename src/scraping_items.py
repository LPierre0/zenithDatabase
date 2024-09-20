from utils import *


def get_item_list_at_lvl(driver, type, lvl, dict_key_item):
    change_level_item(driver, 0, lvl)
    press_research(driver)
    html = get_html(driver)
    soup = get_soup_from_driver(html)
    block_items = soup.find_all('div', {"class": "equipment"})
    
    block_items 
    dict_stat_item = {}

    last_lvl = 0
    for block_item in block_items:
        lvl = block_item.find('div', {"class" : "item-lvl"}).text
        lvl = lvl.replace('Niv. ', '')
        lvl = int(lvl)
        link_to_wakfu = block_item.find('a', {"class" : "item-link"})['href']
        item_name, rarity = get_item_name_and_rarity(block_item)
        img = block_item.find('img', {"class" : "inner-image"})['src']
        img = relink(img)
        if img not in dict_key_item:
            dict_key_item[img] = {}
        dict_key_item[img][rarity] = link_to_wakfu
        if link_to_wakfu not in dict_stat_item:
            dict_stat_item[link_to_wakfu] = (lvl, item_name, rarity, img)
            last_lvl = lvl
    return dict_stat_item, last_lvl, dict_key_item

def get_all_items(driver, type):
    press_item_type(driver, type)
    dict_items = {}
    lvl = LVL_MAX
    last_lvl = 0
    dict_key_item = {}
    while lvl > 1:
        last_lvl = lvl
        dict_to_treat, lvl, dict_key_item_to_treat = get_item_list_at_lvl(driver, type, lvl, dict_key_item)
        dict_items.update(dict_to_treat) 
        dict_key_item.update(dict_key_item_to_treat)
        if last_lvl == lvl:
            break
        
    press_item_type(driver, type)
    return dict_items, dict_key_item

def get_json_items():
    url = 'https://www.zenithwakfu.com/builder/f265c'
    driver = get_driver(url, 1)
    list_type = ['Casque', 'Amulette', 'Anneau', 'Plastron', 'Dague', 'Epaulettes', 'Armes 1 Main', 'Armes 2 Mains', 'Ceinture', 'Bottes', 'Cape', 'Bouclier', 'Emblème']
    dict_key_item = {}
    for type in list_type:
        dict_item, dict_key_item_to_treat = get_all_items(driver, type)
        dict_key_item.update(dict_key_item_to_treat)
        save_dict_to_json(dict_item, f'json2/{type}.json')
    save_dict_to_json(dict_key_item, 'json2/key_item.json')


if __name__ == '__main__':
    get_json_items()

