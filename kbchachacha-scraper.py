import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = 'https://www.kbchachacha.com/public/search/list.empty?page='
OUTPUT_CSV = 'kbchachacha_cars.csv'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def scrape_page(page_num):
    url = BASE_URL + str(page_num)
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    cars = []

    for car in soup.select('div.area'):
        try:
            # First visible image in the carousel
            img_tag = car.select_one('div.thumnail img')
            img_url = img_tag['src'] if img_tag else ''
            if img_url.startswith('//'):
                img_url = 'https:' + img_url

            # Title
            title = car.select_one('strong.tit').get_text(strip=True)

            # Year, mileage, location
            spans = car.select('div.data-line span')
            year = spans[0].get_text(strip=True) if len(spans) > 0 else ''
            mileage = spans[1].get_text(strip=True) if len(spans) > 1 else ''
            location = spans[2].get_text(strip=True) if len(spans) > 2 else ''

            # Price
            price_tag = car.select_one('span.price')
            price = price_tag.get_text(strip=True).replace("만원", " 만원") if price_tag else ''

            # Detail page
            link_tag = car.select_one('a.link')
            detail_url = 'https://www.kbchachacha.com' + link_tag['href'] if link_tag else ''

            cars.append({
                'Model': title,
                'Year': year,
                'Mileage': mileage,
                'Location': location,
                'Price': price,
                'ImageURL': img_url,
                'DetailURL': detail_url
            })

        except Exception as e:
            print(f"⚠️ Skipping a car due to error: {e}")
            continue

    return cars

def scrape_all(pages=250):
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['Model', 'Year', 'Mileage', 'Location', 'Price', 'ImageURL', 'DetailURL']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for page in range(1, pages + 1):
            print(f"🔎 Scraping page {page}...")
            cars = scrape_page(page)
            if not cars:
                print(f"⛔ No listings found on page {page}. Stopping.")
                break
            for car in cars:
                writer.writerow(car)
            time.sleep(1)

    print(f"\n✅ Done! Data saved to '{OUTPUT_CSV}'")

if __name__ == '__main__':
    scrape_all()
