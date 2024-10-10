import os
import sys
sys.path.append('/home/pierre/Documents/PersonnalProject/wakfuDb/src')
from utils import *


class Stats_Scraper:

    def __init__(self, driver, path_json):
        self.driver = driver
        self.path_json = path_json
        self.dict_items = get_json(os.path.join(path_json, 'items.json'))

    def get_all_stats_items(self):
        nb_items = len(self.dict_items)
        nb_treated = 0
        for i, link in enumerate(self.dict_items):

            if 'stats' in self.dict_items[link] and "recipe" in self.dict_items[link] and "use_for_craft" in self.dict_items[link]:
                continue
            try:
                self.get_stats_item(link)   
                nb_treated += 1
                progress_bar(nb_treated, nb_items)
            except:
                if not os.path.exists("logs"):
                    os.mkdir("logs")
                with open("logs/error_stats.txt", 'a') as file:
                    file.write(f"Error at link {link}\n")
            
            if i % 100 == 0:
                save_dict_to_json(self.dict_items, os.path.join(self.path_json, 'items.json'))  
            sleep(7)
        save_dict_to_json(self.dict_items, os.path.join(self.path_json, 'items.json'))
            


    def get_stats_item(self, link):
        self.driver.get(link)
        self.soup = get_soup_from_driver(self.driver)
        stats = self.get_stats(link)
        self.dict_items[link]['stats'] = stats
        recipe, use_for_craft = self.get_recipe()
        self.dict_items[link]['recipe'] = recipe
        self.dict_items[link]['use_for_craft'] = use_for_craft

        

    def get_stats(self, link):
        type_item = self.dict_items[link]["type"]

        if 'dagger' in type_item or 'weapon' in type_item:
            all_stats = self.soup.find_all("div", {"class": "ak-container ak-content-list ak-displaymode-col"})[2]
        else:
            all_stats = self.soup.find("div", {"class": "ak-container ak-content-list ak-displaymode-col"})

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
    
    def get_recipe(self):

        self.soup = get_soup_from_driver(self.driver)
        blocks_recipe = self.soup.find_all("div", {"class": "ak-container ak-panel ak-crafts"})

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


def test_stats():
    link = "https://www.wakfu.com/fr/mmorpg/encyclopedie/armures/30253"
    driver = get_driver(link, headless = False)
    sleep(2)
    path_json = 'json'
    stats_scraper = Stats_Scraper(driver, path_json)
    
    stats_scraper.get_stats_item(link)

    print(stats_scraper.dict_items[link])

def main():
    driver = get_driver("https://www.wakfu.com/fr/mmorpg/")
    path_json = 'json'
    sleep(2)
    stats_scraper = Stats_Scraper(driver, path_json)
    stats_scraper.get_all_stats_items()
    driver.quit()
    

if __name__ == '__main__':
    test_stats()