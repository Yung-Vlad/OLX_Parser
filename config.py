import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import converter
from json_writer import all_categories_to_json, write_to_json
from bs4 import BeautifulSoup
import json

main_url = "https://www.olx.ua"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
