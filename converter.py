import requests

response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()

# Getting value of $ and €
for data in response:
    if data["txt"] == "Долар США":
        USD = data["rate"]
    elif data["txt"] == "Євро":
        EUR = data["rate"]


# Function for exchange from $ or € to ₴
def exchange(value, currency):
    value = int(value.replace(currency, '').replace(' ', ''))
    rates = {
        '$': USD,
        '€': EUR
    }

    converted_value = int(value * rates[currency])
    converted_value = "{:,}".format(converted_value).replace(',', ' ')
    return str(converted_value)


# Function for translating month from En into Ua
def translating_month(date):
    months = {
        "January": "січня",
        "February": "лютого",
        "March": "березня",
        "April": "квітня",
        "May": "травня",
        "June": "червня",
        "July": "липня",
        "August": "серпня",
        "September": "вересня",
        "October": "жовтня",
        "November": "листопада",
        "December": "грудня"
    }

    for month in months:
        if month in date:
            return date.replace(month, months[month])
