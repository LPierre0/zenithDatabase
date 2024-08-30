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
import re
import lxml


def get_driver(url):
    user_data_dir = "/home/pierre/.config/google-chrome"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    driver.maximize_window()
    driver.get(url)
    driver.implicitly_wait(10) 
    return driver

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


def press_research(driver):
    try:
        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Rechercher']"))
        )
        search_button.click()
        print("Bouton de recherche cliqué.")
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

def change_level_item(driver, lvl_min = 0, lvl_max = 230):

    first_thumb = driver.find_element(By.CSS_SELECTOR, '.MuiSlider-thumb[data-index="0"]')
    second_thumb = driver.find_element(By.CSS_SELECTOR, '.MuiSlider-thumb[data-index="1"]')

    value_first = first_thumb.get_attribute('aria-valuenow')
    value_second = second_thumb.get_attribute('aria-valuenow')
    print(value_first, value_second)

    while int(value_first) != lvl_min:
        value_moving = int((lvl_min - int(value_first)))
        if value_moving == 1 or value_moving == -1:
            value_moving = value_moving * 2
        actions = ActionChains(driver)
        actions.click_and_hold(first_thumb).move_by_offset(value_moving, 0).release().perform()
        value_first = first_thumb.get_attribute('aria-valuenow')
    sleep(3)
    while int(value_second) != lvl_max:
        value_moving = int((lvl_max - int(value_second)))
        if value_moving == 1 or value_moving == -1:
            value_moving = value_moving * 2
        actions = ActionChains(driver)
        actions.click_and_hold(second_thumb).move_by_offset(value_moving, 0).release().perform()
        value_second = second_thumb.get_attribute('aria-valuenow')




def main():
    url = 'https://www.zenithwakfu.com/builder/f265c'
    driver = get_driver(url)
    change_level_item(driver, 141, 155)
    press_research(driver)
    sleep(5)

    html = driver.page_source
    soup = get_soup(html)
    items = soup.find_all('a', {"class": "item-link"})
    for item in items:
        print(item['href'])
    driver.quit()



if __name__ == '__main__':
    main()