from utils import *
from sql.sql_insert import add_build_dictionnary
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import time
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


def get_all_build_of_page(soup, data_item_key, date_fixed = None, debug = False):
    block_builds = soup.find('div', {"class" : "zn-inner-block"})

    builds = block_builds.find_all('a')
    dico = {}
    for build in builds:
        link = relink(build['href'])
        dico[link] = get_build(build, data_item_key)


        if dico[link]['date'] == datetime.date.today().isoformat():
            if debug:
                print("Today's build found, didn't get it.")
            dico.pop(link)
            continue
        
        elif date_fixed is not None and dico[link]['date'] < date_fixed:
            if debug:
                print("Build too old for the date fixed, didn't get it.")
            dico.pop(link)
            return dico, True
        else :
            if debug: 
                print(f"Build {dico[link]['name']} found.")
            
    return dico, False


def get_nb_pages():
    driver = get_driver("https://www.zenithwakfu.com/builder?page=1", 1)
    sleep(2)
    html = get_html(driver)
    soup = get_soup_from_driver(html)
    pages = soup.find_all("button", {"class" : "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-rounded MuiPaginationItem-textSecondary"})
    nb_pages = 0
    for page in pages:
        if page.text == '':
            continue
        else:
            nb_pages = int(page.text)

    driver.quit()
    return nb_pages


def process_page(url, data_item_key, driver):
    print(f"Treating page {url}")
    driver.get(url)
    sleep(3)
    html = get_html(driver)
    soup = get_soup_from_driver(html)
    dico, end_stade = get_all_build_of_page(soup, data_item_key)
    return dico, end_stade

def get_actual_state():
    if os.path.exists("temp_state.txt"):
        with open("temp_state.txt", 'r') as file:
            temp = file.read()
            if temp:
                nb_lines_treated = int(temp)
                if nb_lines_treated > 0:
                    nb_pages = nb_pages - nb_lines_treated
                    print(f"Temp state found, {nb_lines_treated} page already scraped.")
                    print(f"Remaining pages to scrape: {nb_pages}")
                    return nb_lines_treated
    return 0



def init_driver(max_worker):
    list_driver = []
    for i in range (1, max_worker + 1):
        driver = get_driver("https://www.zenithwakfu.com/builder?page=1", i)
        list_driver.append(driver)
    return list_driver

def get_all_build():
    nb_pages = get_nb_pages()
    if nb_pages == 0:
        print("No page found.")
        return
    print("Number of pages found: ", nb_pages)
    start = time.time()
    dico_all = {}
    data_item_key = get_json('json/key_item.json')
    nb_lines_treated = 1
    if os.path.exists('json/builds.json'):
        dico_all = get_json('json/builds.json')
        nb_lines_treated = get_actual_state()
    

    urls = [f"https://www.zenithwakfu.com/builder?page={i}" for i in range(nb_lines_treated, nb_pages + 1)]

    num_workers = 1
    list_driver = init_driver(max_worker=num_workers)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []

        for i, (url) in enumerate(urls[nb_lines_treated:], start=0):
            # Calculate worker_id, ensuring it wraps between 1 and num_workers (16)
            worker_id = (i % num_workers) + 1
            print(f"Assigned worker_id: {worker_id} for URL {url}")
            
            # Submit the task using the driver corresponding to worker_id
            futures.append(executor.submit(process_page, url, data_item_key, list_driver[worker_id - 1]))

        i = 0
        for future in as_completed(futures):
            i += 1
            try:
                print(f"Estimated time remaining: {((((time.time() - start) / i) * (len(futures) - i)) / 60):.2f} minutes")
                dico, end_state = future.result()
                dico_all.update(dico)

                    
                if end_state:
                    break
            except Exception as e:
                print(f"Error {e} on page {i}")
                actualize_error_file(i)
                continue
    save_dict_to_json(dico_all, f'json/builds.json')


def get_yesterday_date():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days = 1)
    return yesterday.isoformat()

def get_all_build_from_date(date_fixed):
    nb_pages = get_nb_pages()
    if nb_pages == 0:
        print("No page found.")
        return
    print(date_fixed)

    dico_all = {}
    data_item_key = get_json('json/key_item.json')
    for i in range (1, nb_pages + 1):
        print(f"Treating page {i}")
        url = f"https://www.zenithwakfu.com/builder?page={i}"
        for retry in range(5):
            try:
                driver = get_driver(url, 1)
                sleep(1)
                html = get_html(driver)
                soup = get_soup_from_driver(html)
                break

            except Exception as e: 
                print(f"Error {e} on page {i}")
                sleep(5 * retry)
                driver.quit()
                if retry == 4:
                    print("Too many retries, stopping.")
                    raise
        dico, end_state = get_all_build_of_page(soup, data_item_key, date_fixed)
        dico_all.update(dico)
        driver.quit()
        if end_state:
            break
    add_build_dictionnary(dico_all)

if __name__ == "__main__":
    get_all_build()
