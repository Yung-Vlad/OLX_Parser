import requests
from config import *
import json


# Writing to json all the categories in format "category_name: link"
def all_categories_to_json(url):
    # Getting response and creating bs4 object for parsing
    response = requests.get(url, headers)
    src = response.text
    soup = BeautifulSoup(src, "lxml")

    # Parsing all categories
    items = soup.find_all("div", class_="item")
    all_categories = {}
    for item in items:
        cat_name = item.find("span").text
        link = item.find("a")["href"]
        all_categories[cat_name] = link

    # Writing categories to json
    with open("data/all_categories.json", 'w', encoding="utf-8") as file:
        json.dump(all_categories, file, indent=4, ensure_ascii=False)


# Writing all the parsing data to json
def write_to_json(data, name):
    with open(f"data/{name}.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
