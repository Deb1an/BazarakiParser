from bs4 import BeautifulSoup
import requests
import shelve

url = 'https://www.bazaraki.com/real-estate-to-rent/apartments-flats/?lat=34.728081509867415&lng=32.75216048190142&radius=50000&price_max=1500'
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}
req = requests.get(url, headers=headers)
src = req.text

soup = BeautifulSoup(src, 'lxml')

# Количество подходящих объявлений
amount = soup.find('input', class_='js-query-search').get('placeholder').split()[0]

# Ссылка для объявления
link = 'https://www.bazaraki.com'

iterations = int(amount) // 60 + 1

db = shelve.open('add.txt')

i = 0
next_page = 2

for _ in range(0, iterations):
    # Объявления с текущей страницы
    announcements = soup.find('ul', class_='list-simple__output js-list-simple__output') \
        .find_all('li', class_='announcement-container')

    for announcement in announcements:
        if i == int(amount):
            break
        announcement_id = \
            announcement.find('div', class_='announcement-block__favorites js-add-favorites js-favorites-handler')['data-id']
        if announcement_id not in db.keys():
            title = announcement.find('a', class_='announcement-block__title')['content']
            announcement_link = f'{link}{announcement.find("a", class_="announcement-block__title")["href"]}'
            if announcement.find('img'):
                photo_link = announcement.find('img')['src']
            else:
                photo_link = ''
            description = announcement.find('div', class_='announcement-block__description').text.replace('-', '\n')
            location = announcement.find('meta', itemprop='areaServed')['content']
            price = f"{announcement.find('meta', itemprop='price')['content']}" \
                    f" {announcement.find('meta', itemprop='priceCurrency')['content']}"

            db[announcement_id] = {
                'id': announcement_id,
                'title': title,
                'link': announcement_link,
                'photo_link': photo_link,
                'description': description,
                'location': location,
                'price': price
            }
            # Стучать в ТГ
            print('Done!')
        i += 1

    url = url + f'&page={next_page}'
    if next_page <= iterations:
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, 'lxml')
        next_page += 1

print(len(db.keys()))

db.close()
