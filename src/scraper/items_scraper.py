import os
import sys
import time
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root)

sys.path.append(src_path)
print(sys.path)
from utils import *


class Items_Scraper:

    """

    Website : https://www.zenithwakfu.com/


    Class to scrape the items of the website.

    Information scraped : 
        - The name of the item.
        - The rarity of the item.
        - The level of the item.
        - The image of the item.
        - The link to the item to the wakfu website.

    Attributes :
        driver (WebDriver): The driver to scrape the website.
        path_folder_json (str): The path to the folder where we save the json files.

    Methods:


    
    
    """

    def __init__(self, driver, path_folder_json):
        self.driver = driver
        self.path_folder_json = path_folder_json
        self.url = "https://www.zenithwakfu.com/builder/671f4"
        self.lvl_max = 230
        self.lvl_min = 1
        self.tranche_scale = 15


    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the page.

        Return the soup with all items charged
        """
        sleep(2)
        # Locate the section to scroll.
        scrollable_seciton = self.driver.find_element(By.CLASS_NAME, "builder-searcher")
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_seciton)
        while True:
            # Scroll to the bottom of the section.
            self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_seciton)
            time.sleep(4)
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_seciton)
            if new_height == last_height:
                break
            last_height = new_height
        
        soup = get_soup_from_driver(self.driver)
        return soup
    


    def get_item(self, item):
        """
        Get the item from the item div.

        Args:
            item (BeautifulSoup): The item div.

        Returns:
            str, dict | None, None: The link to the item and the dict of the
            item if all the information are present. None, None otherwise.
        """
        link_div = item.find('a', {"class": "item-link"})
        lvl_div = item.find('div', {"class": "item-lvl"})
        rarity_type_div = item.find('div', {"class": "item-display"})
        if not rarity_type_div:
            return None, None
        rarity_type_links = rarity_type_div.find_all('img')
        name_div = item.find('div', {"class": "item-name"})
        img_item = item.find('img', {"class": "inner-image"})
        dict_item = {}
        if not link_div or not lvl_div or not rarity_type_div or not name_div or not img_item:
            return None, None
        if 'href' in link_div.attrs:
            link = link_div['href']
        if 'src' in img_item.attrs:
            dict_item["image"] = img_item['src']
        dict_item["level"] = lvl_div.text.replace('Niv. ', '')
        if "src" in rarity_type_links[0].attrs:
            dict_item["rarity"] = rarity_type_links[0]['src']
        if "src" in rarity_type_links[1].attrs:
            dict_item["type"] = rarity_type_links[1]['src']
        dict_item["name"] = name_div.text
        return link, dict_item

    def get_items(self):
        """
        Get all the items from zenith.
        """
        self.driver.get(self.url)
        press_research(self.driver)
        soup = self.scroll_to_bottom()
        items_wrapper = soup.find('div', {"class": "result-wrapper"})
        if not items_wrapper:
            print("No item found.")
            return None
        
        self.dict_items = {}

        items = items_wrapper.find_all('div', {"class": "equipment"})
        if not items:
            print("No item found.")
            return None
        
        for item in items:
            link, temp_dict_item = self.get_item(item)
            self.dict_items[link] = temp_dict_item
        print("Items got.")
        self.treat_json_out()
    
        save_dict_to_json(self.dict_items, f'{self.path_folder_json}/items.json')

    def treat_json_out(self):
        print("Treat json out.")
        for key in self.dict_items:
            if not self.dict_items[key]:
                continue
            if "rarity" in self.dict_items[key]:
                rarity = self.dict_items[key]["rarity"]
                rarity = rarity.replace("../images/rarity/", "")
                rarity = rarity.replace(".png", "")
                rarity = rarity.strip()
                self.dict_items[key]["rarity"] = rarity
            if "type" in self.dict_items[key]:
                item_type = self.dict_items[key]["type"]
                item_type = item_type.replace("../images/type_items/", "")
                item_type = item_type.replace(".png", "")
                item_type = item_type.strip()
                self.dict_items[key]["type"] = item_type
            if "image" in self.dict_items[key]:
                img = self.dict_items[key]["image"]
                img = img.replace("../", "https://www.zenithwakfu.com/")
                self.dict_items[key]["image"] = img
        print("Items treated.")




    

def main():
    driver = get_driver("https://www.zenithwakfu.com/builder/671f4", headless=False)
    path_folder_json = 'json'
    items_scraper = Items_Scraper(driver, path_folder_json)
    items_scraper.get_items()

if __name__ == '__main__':
    main()
