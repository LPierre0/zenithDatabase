from utils import * 

def get_nb_pages_wakfu(link_page):
    soup = get_soup(link_page)

    soup = soup.find("ul", {"class": "ak-pagination pagination ak-ajaxloader"})
    if soup is None:
        return 1
    next = False
    for li in soup.find_all("li"):
        text = li.text
        if next:
            text = int(text.strip())
            return text
        if "..." in text:
            next = True
    return 

def get_type_item(soup):
    type_item = soup.find("div", {"class": "ak-encyclo-detail-type col-xs-6"})
    if type_item is None:
        return "No type"
    type_item = type_item.text.strip()
    type_item = type_item.replace("Type :", "")
    if 'Arme' in type_item:
        type_item = type_item.replace('{[~1]?s:}', 's')
    elif "Anneau" in type_item:
        type_item = type_item.replace('{[~1]?x:}', '')
    else:
        type_item = type_item.replace('{[~1]?s:}', '')
    
    return type_item.strip()

def get_item_stats(soup):
    type_item = get_type_item(soup)

    if 'Arme' in type_item:
        all_stats = soup.find_all("div", {"class": "ak-container ak-content-list ak-displaymode-col"})[2]
    else:
        all_stats = soup.find("div", {"class": "ak-container ak-content-list ak-displaymode-col"})

    if all_stats is None:
        return "No stats"

    carac_ligne = all_stats.find_all("div", {"class": "ak-list-element"})
    if carac_ligne is None:
        return
    stats = {}
    for carac_block in carac_ligne:
        carac = carac_block.find("div", {"class": "ak-content"})
        if carac is None:
            continue
        carac = carac.text.strip()
        carac = carac.split(" ")
        quantity = carac[0]
        carac = " ".join(carac[1:])
        stats[carac] = quantity
    return stats

def get_item_recipe(soup):
    blocks_recipe = soup.find_all("div", {"class": "ak-container ak-panel ak-crafts"})

    if blocks_recipe is None:
        return "No recipe", "not use for craft"
    
    recipe = {}
    use_for_craft = []
    for block_recipe in blocks_recipe:

        title = block_recipe.find("div", {"class": "ak-panel-title"}).text.strip()

        if title is None:
            return "No recipe", "not use for craft"
        if title.lower() == "recette":

            elements_recipe = block_recipe.find_all("div", {"class": "ak-list-element"})
            if elements_recipe is None:
                continue

            for element in elements_recipe:
                quantity = element.find("div", {"class": "ak-front"})
                if quantity is None:
                    quantity = 1
                else:
                    quantity = quantity.text
                quantity = quantity.replace("x", "")
                quantity = quantity.strip()
                item = f"https://www.wakfu.com{element.find("a")['href']}"
                recipe[item] = quantity

        elif "est utilisé pour les recettes" == title.lower():
            elements_recipe = block_recipe.find_all("div", {"class": "ak-list-element"})
            if elements_recipe is None:
                continue

            for element in elements_recipe:
                item = f"https://www.wakfu.com{element.find('a')['href']}"
                use_for_craft.append(item)

    if len(recipe) == 0:
        recipe = "No recipe"
    if len(use_for_craft) == 0:
        use_for_craft = "not use for craft"
    return recipe, use_for_craft



def get_item_drop(soup):
    blocks_drop = soup.find_all("div", {"class": "ak-container ak-panel"})
    if blocks_drop is None:
        return "No drop"
    drop = None
    for block in blocks_drop:
        panel_title = block.find("div", {"class": "ak-panel-title"})
        if panel_title is None:
            continue
        if "obtenu" in panel_title.text:
            drop = block
            break
    
    if drop is None:
        return "No drop"
    
    drop = drop.find_all("div", {"class": "ak-column ak-container col-xs-12 col-md-6"})

    if drop is None:
        return "No drop"
    
    dict_drop = {}
    for block in drop:
        link = block.find("a")
        if link is None:
            continue
        url = f"https://www.wakfu.com{link['href']}"
        rate = block.find("div", {"class": "ak-aside"})
        if rate is None:
            rate = "Unknown"
        else:
            rate = rate.text
        dict_drop[url] = rate
    return dict_drop


def get_item_information(url):
    soup = get_soup(url)
    type_item = get_type_item(soup)
    stats = get_item_stats(soup)
    recipe, use_for_craft = get_item_recipe(soup)
    drop = get_item_drop(soup)
    return type_item, stats, recipe, use_for_craft, drop

def get_all_items_information():
    with open("items_link.txt", "r") as file:
        links = file.readlines()
    items = {}
    for link in links:
        try:
            sleep(3)
            link = link.strip()
            print(f"Getting information for {link}")
            type_item, stats, recipe, use_for_craft, drop = get_item_information(link)
            print("Type item: ", type_item)
            if type_item not in items:
                items[type_item] = {}
            items[type_item][link] = (stats, recipe, use_for_craft, drop)
        except Exception as e:
            print(f"An error occurred: {e} on link {link}")
            return

    
    for type_item in items:
        dict_items = get_json(f"json/{type_item}.json")
        new_dict_items = {}
        for link in items[type_item]:
            stats, recipe, use_for_craft, drop = items[type_item][link]
            if link not in new_dict_items:
                new_dict_items[link] = {}
            if link in dict_items:
                new_dict_items[link]["lvl"] = dict_items[link][0]
                new_dict_items[link]["name"] = dict_items[link][1]
                new_dict_items[link]["rarity"] = dict_items[link][2]
                new_dict_items[link]["img"] = dict_items[link][3]
            new_dict_items[link]["stats"] = stats
            new_dict_items[link]["recipe"] = recipe
            new_dict_items[link]["use_for_craft"] = use_for_craft
            new_dict_items[link]["drop"] = drop
            
        save_dict_to_json(new_dict_items, f"jsonSecure/{type_item}.json")
    return items

def get_item_link(soup):
    return soup.find("span", {"class": "ak-linker"}).find("a")["href"]


def relink_wakfu(link):
    link = f"https://www.wakfu.com{link}"
    link = link.split('-')[0]
    return link


def get_all_items_link():
    link_page = "https://www.wakfu.com/fr/mmorpg/encyclopedie/armures?page=1"
    nb_pages = get_nb_pages_wakfu(link_page)
    print(nb_pages)
    items_link = []

    print("Getting all armors link...")
    for i in range(1, nb_pages + 1):
        print(f"Getting page {i}...")
        sleep(2)
        link_page = f"https://www.wakfu.com/fr/mmorpg/encyclopedie/armures?page={i}"
        soup = get_soup(link_page)
        items = soup.find_all("tr", {"class" : "ak-bg-odd"})
        for item in items:
            items_link.append(get_item_link(item))


    link_page = "https://www.wakfu.com/fr/mmorpg/encyclopedie/armes?page=1"
    nb_pages = get_nb_pages_wakfu(link_page)
    print(nb_pages)
    print("Getting all weapons link...")
    for i in range(1, nb_pages + 1):
        print(f"Getting page {i}...")
        sleep(2)
        link_page = f"https://www.wakfu.com/fr/mmorpg/encyclopedie/armes?page={i}"
        soup = get_soup(link_page)
        items = soup.find_all("tr", {"class" : "ak-bg-odd"})
        for item in items:
            items_link.append(get_item_link(item))


    with open("items_link.txt", "w") as file:
        for link in items_link:
            link = relink_wakfu(link)
            file.write(link + "\n")
        
    return items_link



if __name__ == "__main__":
    get_all_items_information()
