import json
import math
import os
from playwright.async_api import async_playwright
import requests

from config import URL, TOKEN, CHAT_ID

DATA_FILE = 'data.json'
CAR_ELEMENTS_COUNT = 24


def clean_data(data):
    cleaned_data = {
        key: value.replace('\xa0', ' ').strip() if isinstance(value, str) else value
        for key, value in data.items()
    }
    cleaned_data['link'] = URL + cleaned_data.get('link', '') if cleaned_data.get('link', '').startswith('/') else cleaned_data.get('link', '')
    return cleaned_data


async def fetch_page_data(page, page_number):
    url = f"{URL}/oferty/offer-type/1/body/station-wagon/brand/toyota/model/corolla/power-from/150/additional/hybrid?strona={page_number}&na-strone={CAR_ELEMENTS_COUNT}"
    await page.goto(url)
    total_elements = await page.inner_text('//*[@id="offers-list"]/div[1]/div[1]/strong')

    cars = []
    for i in range(1, CAR_ELEMENTS_COUNT + 1):
        try:
            car_data = {
                'name': await page.inner_text(f'//*[@id="offers-list"]/div[3]/div[{i}]/div/div[1]/div[1]/span'),
                'price': await page.inner_text(f'//*[@id="offers-list"]/div[3]/div[{i}]/div/div[2]//strong'),
                'production_year': await page.inner_text(f'//*[@id="offers-list"]/div[3]/div[{i}]/div/div[4]/ul/li[1]/span'),
                'millage': await page.inner_text(f'//*[@id="offers-list"]/div[3]/div[{i}]/div/div[4]/ul/li[2]/span'),
                'link': await page.eval_on_selector(f'//*[@id="offers-list"]/div[3]/div[{i}]/a', 'el => el.href')
            }
            cars.append(clean_data(car_data))
        except Exception as e:
            print(f"Error processing car {i}: {e}")

    return int(total_elements.replace(' ', '')), cars


def send_telegram_message(message):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )


async def main():
    previous_data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            previous_data = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        total_elements, first_page_cars = await fetch_page_data(page, 1)
        total_pages = math.ceil(total_elements / CAR_ELEMENTS_COUNT)

        all_cars = first_page_cars
        for page_number in range(2, total_pages + 1):
            cars = await fetch_page_data(page, page_number)
            all_cars.extend(cars)

        await browser.close()

    new_cars = [car for car in all_cars if car not in previous_data]

    if new_cars:
        print("New cars found:")
        for car in new_cars:
            print(car)
            send_telegram_message(f"New car found: {car}")

    with open(DATA_FILE, 'w') as f:
        json.dump(all_cars, f)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
