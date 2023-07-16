from config import *
import asyncio
import aiohttp
import time

parsing_data = []


# Quantity search function pages
async def page_quantity(session, url):
    # Getting response
    response = await session.get(url=url, headers=headers)
    soup = BeautifulSoup(await response.text(), "lxml")

    # Getting quantity
    quantity = soup.find_all("a", class_="css-1mi714g")[-1].text
    return int(quantity)


# Parsing a page with ads
async def parsing_category(session, links, page):
    data = []
    count = 1

    for link in links:
        try:
            # Async request to the link
            async with session.get(url=link, headers=headers) as response:
                src = await response.text()

            # Using selenium for getting seller's phone but requires a captcha
            # with webdriver.Chrome(options) as driver:
            #     driver.get(link)
            #     sleep(1)
            #     driver.find_element(By.CSS_SELECTOR, "[data-cy='dismiss-cookies-overlay']").click()
            #     sleep(1)
            #
            #     # Trying to get the seller's phone number
            #     try:
            #         driver.find_element(By.CSS_SELECTOR, "[data-cy='ad-contact-phone']").click()
            #         sleep(1)
            #         phone_numbers = driver.find_elements(By.CSS_SELECTOR, "[data-testid='contact-phone']")
            #         phone_numbers = ", ".join(list(set([x.text.strip(',').replace(' ', '') for x in phone_numbers])))
            #     except Exception:
            #         print(f"Упссс, щось пішло не так... Можливо сайт запросив пройти 'reKaptcha'")
            #         phone_numbers = None

            soup = BeautifulSoup(src, "lxml")

            # Trying to get title of the ad
            try:
                title = soup.find("h1", attrs={"data-cy": "ad_title"}).text.strip()
            except Exception:
                title = None

            # Trying to get seller's name
            try:
                name_seller = soup.find("h4", class_="css-1lcz6o7 er34gjf0").text.strip()
            except Exception:
                name_seller = None

            # Trying to get publish date
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

            # Trying to get link to main image
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

            print(f"Сторінка #{page}, оголошення #{count} готово...")
            count += 1

        except Exception as e:
            print(f"Сталася помилка при обробці оголошення: {str(e)}")

    parsing_data.append({f"Сторінка #{page}": data})

    print('#' * 30)
    print(f"Сторінка #{page} готово...")
    print('#' * 30)


# Parsing a category
async def get_data(cat_name):
    with open("data/all_categories.json", encoding="utf-8") as file:
        data = json.load(file)

    # Checking name of the category
    if category_name not in data:
        print("Введена невірна назва категорії!")
        exit()

    # Checking exists category in dir /data
    category_path = f"data/{cat_name}.json"
    if os.path.exists(category_path):
        if input("В директорії /data вже є файл з цією категорією\nСпарсити ще раз - Y/y; Відміна - N/n: ") not in 'Yy':
            exit()

    # Using async requests
    async with aiohttp.ClientSession() as session:
        # Getting category url and pages count
        category_url = data[cat_name]
        pages_count = await page_quantity(session, category_url)
        tasks = []

        for page in range(1, pages_count + 1):
            response = await session.get(url=f"{category_url}?page={page}", headers=headers)
            soup = BeautifulSoup(await response.text(), "lxml")

            # Getting all ads on this page
            ads_link = soup.find_all('a', class_="css-rc5s2u")
            ads_link = list(map(lambda x: main_url + x.get("href"), ads_link))

            # Creating tasks
            task = asyncio.create_task(parsing_category(session, ads_link, page))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)


# Main function
if __name__ == '__main__':
    # Checking on exist json-file
    all_cat = "data/all_categories.json"
    if not os.path.exists(all_cat):
        all_categories_to_json(main_url)

    # Open json with cat_name: cat_link
    print("Через декілька секунд відкриється json-файл")
    time.sleep(2)
    os.startfile(os.path.join(os.getcwd(), all_cat))

    # Input cat_name to parsing
    category_name = input("Введіть назву категорії яку бажаєте спарсити: ")

    start_time = time.time()
    asyncio.run(get_data(category_name))

    # Writing to json all the parsing data and opening this file
    write_to_json(parsing_data, category_name)
    os.startfile(os.path.join(os.getcwd(), f"data/{category_name}.json"))

    print(f"Витрачений на виконання скрипта час: {round(time.time() - start_time, 1)}")
