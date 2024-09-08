from utils import *
import datetime

def get_rarity_item(soup):
    classes = soup.get('class')
    for classe in classes:
        if '-item' in classe and not "bg-item" in classe:
            return classe.replace('-item', '')

def get_classe(soup):
    classe = soup.find('img', {"class" : "w-8 h-8 mr-2 items-center justify-center my-auto"}).get('alt')
    return classe

def get_items(soup, data_item_key):
    dico = {}
    block_items = soup.find('div', {"class" : "flex flex-wrap 2xl:flex-nowrap"})
    items = block_items.find_all('div', {"id" : "item-inner-frame"}) 
    if items is None:
        return
    list_type = ['Casque', 'Amulette', 'Plastron', 'Anneau1', 'Anneau2', 'Bottes', 'Cape', 'Epaulettes', 'Ceinture', 'Monture', 'Costume', 'DagueOrBouclierOrArmes', 'Armes', 'Embleme', 'Familier']
    for item, type in zip(items, list_type):
        imgLink = relink(item.find('img')['src'])
        rarity = get_rarity_item(item)
        if imgLink in data_item_key and rarity in data_item_key[imgLink]:
            dico[type] = data_item_key[imgLink][rarity]
        else:
            dico[type] = None
    return dico

def get_lvl(soup):
    lvl = soup.find('div', {"class" : "zn-title"}).text
    lvl = re.findall(r'[0-9]+', lvl)
    if lvl is None:
        return None
    lvl = int(lvl[0])
    return lvl

def get_name(soup):
    return soup.find("span", {"class" : "overflow-ellipsis whitespace-nowrap overflow-hidden"}).text

def get_date(soup):
    date = soup.find('div', {"class" : "text-subtitle text-xs ml-auto self-center"}).text
    date = date.replace('Créé le ', '')
    date = date.replace(':', '')
    date = date.strip()
    date = date.split('-')
    new_date = datetime.date(int(date[2]), int(date[1]), int(date[0]))
    new_date_iso = new_date.isoformat()
    return new_date_iso


def get_build(soup, data_item_key):
    dico = {}
    dico['lvl'] = get_lvl(soup)
    dico['name'] = get_name(soup)
    dico['date'] = get_date(soup)
    dico['classe'] = get_classe(soup)
    dico['items'] = get_items(soup, data_item_key)
    return dico


def get_all_build_of_page(soup, data_item_key):
    block_builds = soup.find('div', {"class" : "zn-inner-block"})

    builds = block_builds.find_all('a')
    dico = {}
    for build in builds:
        link = relink(build['href'])
        dico[link] = get_build(build, data_item_key)
    return dico


def get_nb_pages():
    driver = get_driver("https://www.zenithwakfu.com/builder?page=1")
    html = get_html(driver)
    soup = get_soup(html)
    pages = soup.find_all("button", {"class" : "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-rounded MuiPaginationItem-textSecondary"})
    nb_pages = 0
    for page in pages:
        if page.text == '':
            continue
        else:
            nb_pages = int(page.text)

    driver.quit()
    return nb_pages

def get_all_build():
    nb_pages = get_nb_pages()
    if nb_pages == 0:
        print("No page found.")
        return
    
    dico_all = {}
    data_item_key = get_json('json/key_item.json')
    for i in range (1, nb_pages + 1):
        print(f"Treating page {i}")
        url = f"https://www.zenithwakfu.com/builder?page={i}"
        driver = get_driver(url)
        html = get_html(driver)
        soup = get_soup(html)
        dico = get_all_build_of_page(soup, data_item_key)
        dico_all.update(dico)
        driver.quit()
    save_dict_to_json(dico_all, f'json/builds.json')

if __name__ == "__main__":
    get_all_build()

