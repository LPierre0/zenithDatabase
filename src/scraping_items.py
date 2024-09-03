from utils import *


def get_item_list_at_lvl(driver, type, lvl):
    change_level_item(driver, 0, lvl)
    press_research(driver)
    html = get_html(driver)
    soup = get_soup(html)
    block_items = soup.find_all('div', {"class": "equipment w-full sm:w-1/2-gap-1 md:w-1/2-gap-1 lg:w-full-gap-1 xl:w-1/2-gap-1 2xl:w-2/6-gap-1 flex flex-col"})
    dict = {}
    last_lvl = 0
    for block_item in block_items:
        lvl = block_item.find('div', {"class" : "item-lvl"}).text
        lvl = lvl.replace('Niv. ', '')
        lvl = int(lvl)
        link_to_wakfu = block_item.find('a', {"class" : "item-link"})['href']
        item_name, rarity = get_item_name_and_rarity(block_item)
        img = block_item.find('img', {"class" : "inner-image"})['src']
        img = img.replace('..', 'https://www.zenithwakfu.com')
        if link_to_wakfu not in dict:
            dict[link_to_wakfu] = (lvl, item_name, rarity, img)
            last_lvl = lvl
    return dict, last_lvl

def get_all_items(driver, type):
    press_item_type(driver, type)
    dict_items = {}
    lvl = LVL_MAX
    last_lvl = 0
    while lvl > 1:
        last_lvl = lvl
        dict_to_treat, lvl = get_item_list_at_lvl(driver, type, lvl)
        dict_items.update(dict_to_treat) 
        if last_lvl == lvl:
            break
        
    press_item_type(driver, type)
    return dict_items

def get_json_items():
    url = 'https://www.zenithwakfu.com/builder/f265c'
    driver = get_driver(url)
    list_type = ['Casque', 'Amulette', 'Anneau', 'Plastron', 'Dague', 'Armes 1 Main', 'Armes 2 Mains', 'Ceinture', 'Bottes', 'Cape', 'Bouclier', 'Emblème']
    list_type = ['Familier', 'Monture']
    for type in list_type:
        dict_item = get_all_items(driver, type)
        save_dict_to_json(dict_item, f'json/{type}.json')


if __name__ == '__main__':
    get_json_items()