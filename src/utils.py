import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import lxml


def get_driver(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(1) 
    return driver

def get_soup(html):
    return bs4.BeautifulSoup(html, 'lxml')

def is_build_page(url):
    return bool(re.match(r'^https://www.zenithwakfu.com/builder/[a-zA-Z0-9]*', url))



def accept_cookies(driver):
    try:
        # Attendre que le bouton d'autorisation soit visible et cliquable
        consent_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//p[@class='fc-button-label' and text()='Autoriser']"))
        )
        # Cliquer sur le bouton
        consent_button.click()
        print("Bouton d'autorisation cliqué.")
    except TimeoutException:
        print("Le bouton d'autorisation n'est pas apparu dans le délai spécifié.")

def change_level_item(driver, is_build_page, lvl_min = 0, lvl_max = 230):
    if is_build_page:
        ratio = 194/181
    else:
        ratio = 50/35
    first_thumb = driver.find_element(By.CSS_SELECTOR, '.MuiSlider-thumb[data-index="0"]')
    second_thumb = driver.find_element(By.CSS_SELECTOR, '.MuiSlider-thumb[data-index="1"]')

    print(first_thumb, second_thumb)
    initial_value_first = first_thumb.get_attribute('aria-valuenow')
    initial_value_second = second_thumb.get_attribute('aria-valuenow')
    print(initial_value_first, initial_value_second)

    value_to_move_first = int((lvl_min - int(initial_value_first)) * ratio) + 1
    value_to_move_second = int((lvl_max - int(initial_value_second)) * ratio) - 2
    print(value_to_move_first, value_to_move_second)
    actions = ActionChains(driver)
    actions.click_and_hold(first_thumb).move_by_offset(value_to_move_first, 0).release().perform()
    actions.click_and_hold(second_thumb).move_by_offset(value_to_move_second, 0).release().perform()

    new_value_first = first_thumb.get_attribute('aria-valuenow')
    new_value_second = second_thumb.get_attribute('aria-valuenow')
    print(f'Nouvelle valeur du premier curseur: {new_value_first}')
    print(f'Nouvelle valeur du deuxième curseur: {new_value_second}')



def main():
    url = 'https://www.zenithwakfu.com/builder/f265c'
    build_page_bool = is_build_page(url)
    driver = get_driver(url)

    accept_cookies(driver)
    change_level_item(driver, is_build_page, 66, 95)

if __name__ == '__main__':
    main()