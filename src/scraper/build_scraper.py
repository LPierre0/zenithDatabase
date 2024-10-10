import datetime
import sys
import os
sys.path.append('/home/pierre/Documents/PersonnalProject/wakfuDb/src')
from utils import *

class Builder_Scrapper:

    def __init__(self, driver, path_bdd, path_json_output, date_fixed, debug) -> None:
        self.driver = driver
        self.path_bdd = path_bdd
        self.soup = None
        self.path_json_output = path_json_output
        self.date_fixed = date_fixed
        self.dict_build = get_json(os.path.join(path_json_output, 'builds.json'))
        self.data_item_key = get_json(os.path.join(path_json_output, 'key_item.json'))
        self.dict_items = get_json(os.path.join(path_json_output, 'items.json'))
        self.debug = debug

    def relink(self, link) -> str:
        """
        Relink the link of the image.

        Args:
            link (str): The link of the image.

        Returns:
            str: The new link of the image.
        """
        return link.replace('../', 'https://www.zenithwakfu.com/')

        
    def get_all_build_of_page(self) -> bool:
        """
        Get all the build of the page.

        Returns:
            bool: True if we need to stop the scrapping, False otherwise.
        """

        self.soup = get_soup_from_driver(self.driver)

        block_builds = self.soup.find('div', {"class" : "zn-inner-block"})
        if block_builds is None:
            print("In function get_all_build_of_page, block_builds is None.")
            return True
        
        builds = block_builds.find_all('a')
        if builds is None:
            print("In function get_all_build_of_page, builds is None.")
            return True
        
        for build in builds:
            link = relink(build['href'])
            self.soup_current_build = build
            current_dict_build = self.get_build()
            self.dict_build[link] = current_dict_build


            if self.dict_build[link]['date'] == datetime.date.today().isoformat():
                if self.debug:
                    print("Today's build found, didn't get it.")
                self.dict_build.pop(link)
                continue
            
            elif self.date_fixed is not None and self.dict_build[link]['date'] < self.date_fixed:
                if self.debug:
                    print("Build too old for the date fixed, didn't get it.")
                self.dict_build.pop(link)
                return True
            else :
                if self.debug: 
                    print(f"Build {self.dict_build[link]['name']} found.")
                
        return False
    
    def get_build(self) -> dict:
        """
        Get the build of the page from the soup of the current build.

        Returns:
            dict: The build of the page.
        """

        dico = {}
        dico['lvl'] = get_lvl(self.soup_current_build)
        dico['name'] = get_name(self.soup_current_build)
        dico['date'] = get_date(self.soup_current_build)
        dico['classe'] = get_classe(self.soup_current_build)
        dico['items'] = self.get_items()
        return dico
    

    def get_items(self) -> dict | None:
        """
        Get the items of the build.

        Returns:
            dict | None: The items of the build.
        
        The key of the dict is the type of the item

        """
        dict_item_of_build = {}
        block_items = self.soup_current_build.find('div', {"class" : "flex flex-wrap 2xl:flex-nowrap"})

        if block_items is None:
            return None
        
        items = block_items.find_all('div', {"id" : "item-inner-frame"}) 
        if items is None:
            return None
        self.data_item_key = {}
        nb_ring = 1
        for item in items:
            imgLink = self.relink(item.find('img')['src'])
            rarity = get_rarity_item(item)
            print(f"Item {imgLink} found.")
            print(f"Rarity: {rarity}")
            if imgLink not in self.data_item_key:
                self.data_item_key[imgLink] = {}
            if rarity not in self.data_item_key[imgLink]:
                link_item = get_wakfu_link(imgLink, rarity, self.dict_items)
                self.data_item_key[imgLink][rarity] = link_item
            link_item = self.data_item_key[imgLink][rarity]
            if link_item is None:   
                continue
            type_item = self.dict_items[link_item]["type"]
            if type_item == "ring":
                type_item = f"ring_{nb_ring}"
                nb_ring += 1
            dict_item_of_build[type_item] = self.data_item_key[imgLink][rarity]
        return dict_item_of_build



    def get_soup(self) -> None:
        self.soup = get_soup_from_driver(self.driver)



    def preprocess_page(self) -> None:
        """
        Preprocess the page.
        """
        print(f"Preprocessing page {self.current_url}")
        print(type(self.driver))
        self.driver.get(self.current_url)
        print("Page loaded.")
        sleep(2)
        print("Sleep done.")
        print("Getting soup.")
        self.get_soup()
        print("Soup got.")
        print("Getting all build of the page.")
        self.get_all_build_of_page()



    def get_all_build(self) -> None:
        nb_pages = get_nb_pages(self.driver)
        if nb_pages == 0:
            print("No page found.")
            return None
        print("Number of pages found: ", nb_pages)

        dico_all = {}
        self.data_item_key = get_json('json/key_item.json')
        nb_lines_treated = 1
        if os.path.exists('json/builds.json'):
            dico_all = get_json('json/builds.json')

        nb_lines_treated = get_nb_page_scrapped()
        print(f"Temp state found, {nb_lines_treated} page already scraped.")
        print(f"Remaining pages to scrape: {nb_pages}")
        for i in range (nb_lines_treated, nb_pages + 1):
            try : 
                self.current_url = f"https://www.zenithwakfu.com/builder?page={i}"
                self.preprocess_page()
                if i % 1000 == 0:
                    save_dict_to_json(dico_all, self.path_json_output)
                    with open("temp_state_build.txt", 'a') as file:
                        file.write(str(i))
                
            except Exception as e:
                print(f"Error {e} on page {i}")
                actualize_error_file(i)
                continue

        save_dict_to_json(dico_all, f'json/builds.json')
    

def get_rarity_item(soup) -> str | None:
    """
    Return the rarity of the item.

    Args:
        soup (BeautifulSoup): The soup of the item.

    Returns:
        str | None: The rarity of the item.

    The rarity is in the class name in the form of 'bg-item-rarity'.
    """
    classes = soup.get('class')
    for classe in classes:
        if '-item' in classe and not "bg-item" in classe:
            return classe.replace('-item', '')
    return None
    
def get_classe(soup) -> str | None:
    """
    Return the class of the build.

    Args:
        soup (BeautifulSoup): The soup of the build.

    Returns:
        str | None: The class of the build.
    """

    classe = soup.find('img', {"class" : "w-8 h-8 mr-2 items-center justify-center my-auto"}).get('alt')
    return classe


def get_lvl(soup):
    """
    Return the level of the build.
    
    Args:
        soup (BeautifulSoup): The soup of the build.
        
    Returns:
        int | None: The level of the build.
    """
    lvl = soup.find('div', {"class" : "zn-title"}).text
    lvl = re.findall(r'[0-9]+', lvl)
    if lvl is None:
        return None
    lvl = int(lvl[0])
    return lvl

def get_name(soup):
    """
    Return the name of the build.

    Args:
        soup (BeautifulSoup): The soup of the build.

    Returns:
        str: The name of the build.
    """
    return soup.find("span", {"class" : "overflow-ellipsis whitespace-nowrap overflow-hidden"}).text

def get_date(soup):
    """
    Return the date of the build.

    Args:
        soup (BeautifulSoup): The soup of the build.
    
    Returns:
        str: The date of the build.
    """
    date = soup.find('div', {"class" : "text-subtitle text-xs ml-auto self-center"}).text
    date = date.replace('Créé le ', '')
    date = date.replace(':', '')
    date = date.strip()
    date = date.split('-')
    new_date = datetime.date(int(date[2]), int(date[1]), int(date[0]))
    new_date_iso = new_date.isoformat()
    return new_date_iso

def get_nb_pages(driver):
    """
    Get the number of pages to scrap.

    Returns:
        int: The number of pages to scrap.
    """
    driver.get("https://www.zenithwakfu.com/builder?page=1")
    sleep(2)
    soup = get_soup_from_driver(driver)
    pages = soup.find_all("button", {"class" : "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-rounded MuiPaginationItem-textSecondary"})
    nb_pages = 0
    for page in pages:
        if page.text == '':
            continue
        else:
            nb_pages = int(page.text)
    return nb_pages

def get_nb_page_scrapped():
    """
    Read the temp_state.txt file to get the number of page already scrapped.

    Returns:
        int: The number of page already scrapped.
    """
    if os.path.exists("temp_state_build.txt"):
        with open("temp_state_build.txt", 'r') as file:
            temp = file.read()
            if temp:
                return int(temp)
    return 0

def get_wakfu_link(imgLink, rarity, dict_items):
    """
    Get the wakfu link of the item.

    Args:
        imgLink (str): The link of the image of the item.
        rarity (str): The rarity of the item.
        dict_items (dict): The dict of the items.

    Returns:
        str | None: The link of the item in wakfu.
    """
    for key in dict_items:
        if imgLink == dict_items[key]["image"] and rarity == dict_items[key]["rarity"]:
            return key
    return None
            


def test_one_page():
    driver = get_driver("https://www.zenithwakfu.com/builder?page=100", headless=False)
    path_bdd = ''
    path_json_output = 'json/'
    date_fixed = None
    debug = False
    builder_scrapper = Builder_Scrapper(driver, path_bdd, path_json_output, date_fixed, debug)
    sleep(2)
    builder_scrapper.get_all_build_of_page()
    save_dict_to_json(builder_scrapper.dict_build, 'json/test_builds.json')
    driver.quit()

def test():
    driver = get_driver("https://www.zenithwakfu.com/builder?page=1", headless=False)
    path_bdd = ''
    path_json_output = 'json/'
    date_fixed = None
    debug = False
    builder_scrapper = Builder_Scrapper(driver, path_bdd, path_json_output, date_fixed, debug)

    builder_scrapper.get_all_build()
    driver.quit()

if __name__ == "__main__":
    test_one_page()