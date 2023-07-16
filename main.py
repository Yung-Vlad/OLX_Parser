import requests
from config import *


# Quantity search function pages
def page_quantity(cat_name):
    # Getting response
    response = requests.get(cat_name)
    src = response.text
    soup = BeautifulSoup(src, "lxml")

    # Getting quantity
    quantity = soup.find_all("a", class_="css-1mi714g")[-1].text
    return int(quantity)


# Parsing a page with ads
def parsing_category(links):
    data = []
    count = 1

    for link in links:
        src = requests.get(link, headers).text
        # with webdriver.Chrome(options) as driver:
        #     driver.get(link)
        #     sleep(1)
        #     driver.find_element(By.CSS_SELECTOR, "[data-cy='dismiss-cookies-overlay']").click()
        #     sleep(1)
        #     src = driver.page_source
        #
        #     # Trying to get the seller's phone number
        #     try:
        #         driver.find_element(By.CSS_SELECTOR, "[data-cy='ad-contact-phone']").click()
        #         sleep(1)
        #         phone_numbers = driver.find_elements(By.CSS_SELECTOR, "[data-testid='contact-phone']")
        #         phone_numbers = ", ".join(list(set([x.text.strip(',').replace(' ', '') for x in phone_numbers])))
        #     except Exception:
        #         print(f"Упссс, щось пішло не так... Можливо сайт запросив пройти 'reKaptcha'")

        soup = BeautifulSoup(src, "lxml")
        try:
            title = soup.find("h1", attrs={"data-cy": "ad_title"}).text.strip()
        except Exception:
            title = None

        try:
            name_seller = soup.find("h4", class_="css-1lcz6o7 er34gjf0").text.strip()
        except Exception:
            name_seller = None

        try:
            publish_date = soup.find("span", attrs={"data-cy": "ad-posted-at"}).text
            if "сьогодні" in publish_date.lower():
                publish_date = converter.translating_month(datetime.now().strftime("%d %B %Y р."))
        except Exception:
            publish_date = None

        # Trying to get price and exchange to UAH if it needed
        try:
            price = soup.find("h2", class_="css-5ufiv7 er34gjf0").text.strip()
            if '€' in price:
                price = converter.exchange(price, '€') + ' грн'
            elif '$' in price:
                price = converter.exchange(price, '$') + ' грн'
        except Exception:
            price = None

        try:
            main_img = soup.find("img", attrs={"data-testid": "swiper-image"})["src"]
        except Exception:
            main_img = None

        data.append(
            {
                "Назва": title,
                "Посилання на оголошення": link,
                "Посилання на головне зображення": main_img,
                "Ім'я продавця:": name_seller,
                # "Контакти": phone_numbers if phone_numbers else None,
                "Дата публікації": publish_date,
                "Ціна": price
            }
        )

        print(f"Оголошення #{count} готово...")
        count += 1

    return data


# Parsing a category
def get_data(cat_name):
    with open("data/all_categories.json", encoding="utf-8") as file:
        data = json.load(file)

    # Checking name of the category
    if category_name not in data:
        print("Введена невірна назва категорії!")
        return

    # Checking exists category in dir /data
    category_path = f"data/{cat_name}.json"
    if os.path.exists(category_path):
        if input("В директорії /data вже є файл з цією категорією\nСпарсити ще раз - Y/y; Відміна - N/n: ") not in 'Yy':
            return

    # Getting category url and pages count
    category_url = data[cat_name]
    pages_count = page_quantity(category_url)

    parsing_data = []
    for i in range(1, pages_count):
        response = requests.get(f"{category_url}?page={i}")
        src = response.text
        soup = BeautifulSoup(src, "lxml")

        # Getting all ads on this page
        ads_link = soup.find_all('a', class_="css-rc5s2u")
        ads_link = list(map(lambda x: main_url + x.get("href"), ads_link))

        # Adding the parsing data
        parsing_data.append({f"Page #{i}": parsing_category(ads_link)})
        print(f"Сторінка #{i} готово...")

    # Writing to json all the parsing data and returning absolute path to this json
    write_to_json(parsing_data, cat_name)
    return os.path.join(os.getcwd(), category_path)


# Main function
if __name__ == '__main__':
    # Checking on exist json-file
    all_cat = "data/all_categories.json"
    if not os.path.exists(all_cat):
        all_categories_to_json(main_url)

    # Open json with cat_name: cat_link
    # print("Через декілька секунд відкриється json-файл")
    # sleep(2)
    # os.startfile(os.path.join(os.getcwd(), all_cat))

    # Input cat_name to parsing and opening json with the result
    category_name = input("Введіть назву категорії яку бажаєте спарсити: ")
    os.startfile(get_data(category_name))
