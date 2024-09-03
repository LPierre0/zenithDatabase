import json
from time import sleep
import bs4
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import re
import lxml

LVL_MAX = 230

def concat_list(list1, list2):
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1

def get_driver(url, headless = True):
    user_data_dir = "/home/pierre/.config/google-chrome"

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.maximize_window()
    driver.get(url)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.implicitly_wait(10) 
    return driver

def get_html(driver):
    sleep(2)
    return driver.page_source

def get_soup(html):
    return bs4.BeautifulSoup(html, 'lxml')

def is_build_page(url):
    return bool(re.match(r'^https://www.zenithwakfu.com/builder/[a-zA-Z0-9]*', url))

def remove_popups(driver):
    try:
        close_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'close-button-class')]"))
        )
        close_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("Pop-up not found or did not appear in the specified time frame.")

def press_item_type(driver, item_type):
    try:
        item_type_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'MuiIconButton-root') and .//img[contains(@alt, '{item_type}')]]"))
        )
        item_type_button.click()
        print(f"Bouton de type d'item {item_type} cliqué.")
        sleep(1)
    except TimeoutException:
        print(f"Le bouton de type d'item {item_type} n'est pas apparu dans le délai spécifié.")

def press_research(driver):
    try:
        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Rechercher']"))
        )
        search_button.click()
        print("Bouton de recherche cliqué.")
        sleep(2)
    except TimeoutException:
        print("Le bouton de recherche n'est pas apparu dans le délai spécifié.")


def accept_cookies(driver):
    try:
        consent_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//p[@class='fc-button-label' and text()='Autoriser']"))
        )
        consent_button.click()
        print("Bouton d'autorisation cliqué.")
    except TimeoutException:
        print("Le bouton d'autorisation n'est pas apparu dans le délai spécifié.")

def get_item_name_and_rarity(block_item):
    item = block_item.find('div', {"class" : "item-name"})
    item_name = item.text
    rarity = item["class"][1]
    rarity = rarity.replace('-item', '')
    return item_name, rarity


def ajust_thumb(driver, thumb, nb_move, start_value, objective_value, sleep_time=0.02):
    actions = ActionChains(driver)
    print(f"Moving thumb from {start_value} to {objective_value}")
    print(f"Nb move: {nb_move}")
    if nb_move == 0:
        return
    actions.click(thumb).perform()
    if nb_move > 0:
        for i in range(0, nb_move):
            actions.send_keys(Keys.ARROW_RIGHT).perform()
            sleep(sleep_time)
    else:
        for i in range(-nb_move):
            actions.send_keys(Keys.ARROW_LEFT).perform()
            sleep(sleep_time)
    if int(thumb.get_attribute('aria-valuenow')) != objective_value:
        actions.send_keys(Keys.ARROW_RIGHT).perform()
        new_start_value = int(thumb.get_attribute('aria-valuenow'))
        ajust_thumb(driver, thumb, objective_value - new_start_value, new_start_value, objective_value, sleep_time = sleep_time * 2)

def change_level_item(driver, lvl_min = 0, lvl_max = LVL_MAX):

    first_thumb = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.MuiSlider-thumb[data-index="0"]'))
    )
    second_thumb = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.MuiSlider-thumb[data-index="1"]'))
    )
    
    value_first = first_thumb.get_attribute('aria-valuenow')
    value_second = second_thumb.get_attribute('aria-valuenow')

    if value_first and value_second:
        value_first = int(value_first)
        value_second = int(value_second)
    else:
        print("Error: could not get values from thumbs.")
        return

    print(f"Starting values: {value_first}, {value_second}, goal values: {lvl_min}, {lvl_max}")
    

    nb_move_first = lvl_min - value_first
    nb_move_second = lvl_max - value_second
    print(nb_move_first, nb_move_second)
    ajust_thumb(driver, first_thumb, nb_move_first, value_first, lvl_min)
    ajust_thumb(driver, second_thumb, nb_move_second, value_second, lvl_max)

    print(f"Final values: {first_thumb.get_attribute('aria-valuenow')}, {second_thumb.get_attribute('aria-valuenow')}")
    sleep(1)



def save_dict_to_json(dict, filename):
    with open (filename, 'w') as file:
        json.dump(dict, file, indent=4, ensure_ascii=False)

def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def relink(url):
    if '../' in url:
        url = url.replace('..', '')
    return f"https://www.zenithwakfu.com{url}"

def test_slider():
    driver = get_driver('https://www.zenithwakfu.com/builder/f265c')
    change_level_item(driver, 0, 230)
    change_level_item(driver, 0, 100)
    change_level_item(driver, 0, 50)
    change_level_item(driver, 0, 78)

    sleep(5)
    driver.quit()


