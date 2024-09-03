from utils import *


def get_rarity_item(soup):
    classes = soup.get('class')
    for classe in classes:
        if '-item' in classe and not "bg-item" in classe:
            return classe.replace('-item', '')

def get_classe(soup):
    classe = soup.find('img', {"class" : "w-8 h-8 mr-2 items-center justify-center my-auto"}).get('alt')
    return classe

def get_items(soup):
    dico = {}
    block_items = soup.find('div', {"class" : "flex flex-wrap 2xl:flex-nowrap"})
    items = block_items.find_all('div', {"id" : "item-inner-frame"}) 
    if items is None:
        return
    list_type = ['Casque', 'Amulette', 'Plastron', 'Anneau1', 'Anneau2', 'Bottes', 'Cape', 'Epaulettes', 'Ceinture', 'Monture', 'Costume', 'DagueOrBouclierOrArmes', 'Armes', 'Embleme', 'Familier']
    for item, type in zip(items, list_type):
        dico[type] = (relink(item.find('img')['src']), get_rarity_item(item))
    return dico

def get_lvl(soup):
    return soup.find('div', {"class" : "zn-title"}).text

def get_name(soup):
    return soup.find("span", {"class" : "overflow-ellipsis whitespace-nowrap overflow-hidden"}).text

def get_date(soup):
    return soup.find('div', {"class" : "text-subtitle text-xs ml-auto self-center"}).text


def get_build(soup):
    dico = {}
    dico['lvl'] = get_lvl(soup)
    dico['name'] = get_name(soup)
    dico['date'] = get_date(soup)
    dico['classe'] = get_classe(soup)
    dico['items'] = get_items(soup)
    return dico


def get_all_build_of_page(soup):
    block_builds = soup.find('div', {"class" : "zn-inner-block"})

    builds = block_builds.find_all('a')
    dico = {}
    for build in builds:
        link = relink(build['href'])
        dico[link] = get_build(build)

    return dico

def get_all_build():
    driver = get_driver("https://www.zenithwakfu.com/builder?page=1")
    html = get_html(driver)
    soup = get_soup(html)
    pages = soup.find_all("button", {"class" : "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-rounded MuiPaginationItem-textSecondary"})
    nbPage = 0
    for page in pages:
        if page.text == '':
            continue
        else:
            nbPage = int(page.text)
    if nbPage == 0:
        print("No page found.")
        return
    
    driver.quit()
    dico_all = {}
    for i in range (1, nbPage + 1):
        print(f"Treating page {i}")
        url = f"https://www.zenithwakfu.com/builder?page={i}"
        driver = get_driver(url)
        html = get_html(driver)
        soup = get_soup(html)
        dico = get_all_build_of_page(soup)
        dico_all.update(dico)
        driver.quit()
    save_dict_to_json(dico_all, f'json/builds.json')

if __name__ == "__main__":
    get_all_build()