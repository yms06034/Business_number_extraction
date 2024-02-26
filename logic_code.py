from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as BS
from datetime import datetime

import pandas as pd
import time
import sys, os
import re
import json, requests
import math, openpyxl


def find_css(css_selector, browser):
    return browser.find_element(By.CSS_SELECTOR, css_selector)
def finds_css(css_selector, browser):
    return browser.find_elements(By.CSS_SELECTOR, css_selector)

def find_xpath(xpath, browser):
    return browser.find_element(By.XPATH, xpath)
def finds_xpath(xpath, browser):
    return browser.find_elements(By.XPATH, xpath)

def find_id(e_id, browser):
    return browser.find_element(By.ID, e_id)

def find_className(cn, browser):
    return browser.find_element(By.CLASS_NAME, cn)
def finds_className(cn , browser):
    return browser.find_elements(By.CLASS_NAME, cn)

def find_linktext(lt, browser):
    return browser.find_element(By.LINK_TEXT, lt)

def find_name(name, browser):
    return browser.find_element(By.NAME, name)
def finds_name(name, browser):
    return browser.find_elements(By.NAME, name)

def find_tagName(tag_name, browser):
    return browser.find_element(By.TAG_NAME, tag_name)

def finds_tagName(tag_name, browser):
    return browser.find_elements(By.TAG_NAME, tag_name)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--no--sandbox')
    options.add_argument('no-sandbox')
    options.add_argument('--disable-dev-shm-suage')
    options.add_argument('--window-size=1080,800')
    options.add_argument('incognito')
    chrome_service = Service('chromedriver')
    chrome_service = Service(executable_path='chromedriver.exe')
    
    browser = webdriver.Chrome(service=chrome_service, options=options)
    
    return browser

def ka_open_url(browser):
    browser.get(f'https://map.kakao.com/')
    browser.implicitly_wait(2)

def search_keyword(browser, ka_kw):
    find_id('search.keyword.query', browser).clear()
    find_id('search.keyword.query', browser).send_keys(ka_kw)
    time.sleep(1)
    find_id('search.keyword.query', browser).send_keys('\n')
    time.sleep(1)

    # FInd info.search.place.Count
    try:
        place_cnt = find_id('info.search.place.cnt', browser).text
        return place_cnt
    except:
        return 0
    # place_cnt = place_cnt.replace(',', '')
    # place_cnt = int(place_cnt)
    # place_cnt = math.ceil(place_cnt/15)
    # place_cnt = math.ceil(place_cnt/5)


def find_id_list_excetion():
    find_id_list = []

    for _ in range(1, 150):
        for i in range(1, 6):
            find_id_list.append(f'info.search.page.no{i}')
            if i % 5 == 0:
                find_id_list.append('info.search.page.next')
                
    final_find_id_list = [item for item in find_id_list if item != 'info.search.page.no1']

    return final_find_id_list

def final_logic(browser, ka_kw):
    ka_open_url(browser)
    time.sleep(1)
    re = search_keyword(browser, ka_kw)
    if re != 0:
        time.sleep(1)
        final_find_id_list = find_id_list_excetion()
        time.sleep(1)

        name_list = []
        category_list = []
        tel_list = []
        addr_list = []

        soup = BS(browser.page_source, 'html.parser')

        for shop_name in soup.find_all(class_='link_name'):
            name_list.append(shop_name.text)

        for shop_category in soup.find_all(class_='subcategory clickable'):
            category_list.append(shop_category.text)

        for shop_tel in soup.find_all(class_='phone'):
            tel_list.append(shop_tel.text)    

        for shop_addr in soup.find_all(class_='addr'):
            addr_list.append(shop_addr.text)

        browser.execute_script("document.getElementById('info.search.place.more').click();")

        count = 1
        dt = datetime.now().strftime("%Y-%m-%d")
        folder = f'{dt} DB'
        if not os.path.exists(folder):
            os.makedirs(folder)

        try:
            for idx, text in enumerate(final_find_id_list):
                time.sleep(1)
                soup = BS(browser.page_source, 'html.parser')

                for shop_name in soup.find_all(class_='link_name'):
                    name_list.append(shop_name.text)

                for shop_category in soup.find_all(class_='subcategory clickable'):
                    category_list.append(shop_category.text)

                for shop_tel in soup.find_all(class_='phone'):
                    tel_list.append(shop_tel.text)    

                for shop_addr in soup.find_all(class_='addr'):
                    addr_list.append(shop_addr.text)

                browser.execute_script(f"document.getElementById('{text}').click();")

                count += 1
                if count == 34:
                    break
        except:
            df = pd.DataFrame({
                "name": name_list,
                "category": category_list,
                "tel": tel_list,
                "addr": addr_list,
            })

            df.to_excel(f'{folder}/{ka_kw} 전화번호 DB.xlsx', index=False)
            return 2

        time.sleep(1)
        df = pd.DataFrame({
            "name": name_list,
            "category": category_list,
            "tel": tel_list,
            "addr": addr_list,
        })

        df.to_excel(f'{folder}/{ka_kw} 전화번호 DB.xlsx', index=False)
    else:
        return 0
    
    return 1