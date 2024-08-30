import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import re
import lxml



chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(options=chrome_options)

driver.get('https://zenithwakfu.com/builder')

driver.implicitly_wait(1) 

rendered_html = driver.page_source

driver.quit()

soup = bs4.BeautifulSoup(rendered_html, 'lxml')
lvl = soup.findAll('div', {'class' : "zn-title"})
for lv in lvl:
    print(lv.text)
