import requests
from bs4 import BeautifulSoup
import csv
import codecs


def get_gtml(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = soup.find('div', class_ = 'pagination-pages').find_all('a', class_ = 'pagination-page')[-1].get('href')
        total_pages = pages.split('=')[1].split('&')[0]
    except Exception as e:
        total_pages = 1

    return int(total_pages)

def write_csv(data):
    with codecs.open('avito.csv', 'a', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow((data['title'], data['price'], data['metro'], data['url']))

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    ads = soup.find('div', class_='catalog-list').find_all('div', class_ = 'item_table')
    for ad in ads:
        try:
            title = ad.find('div', class_= 'description').find('h3').text.strip()
        except:
            title = ''
        try:
            url = 'https://www.avito.ru' + ad.find('div', class_= 'description').find('h3').find('a').get('href')
        except:
            url = ''
        try:
            price = ad.find('div', class_='about').text.strip().encode().decode('utf-8', 'ignore')
        except:
            price = ''
        try:
            metro = ad.find('div', class_ = 'data').find_all('p')[-1].text.strip().encode().decode('utf-8', 'ignore')
        except:
            metro = ''
        data = {'title':title,
                'price':price,
                'metro': metro,
                'url': url}
        write_csv(data)


def main():
    url = 'https://www.avito.ru/sankt-peterburg/produkty_pitaniya?p=2&user=1&q=%D1%80%D1%8B%D0%B1%D0%B0'
    base_url = 'https://www.avito.ru/sankt-peterburg/produkty_pitaniya?'
    page_part = 'p='
    query_part = '&user=1&q=%D1%80%D1%8B%D0%B1%D0%B0'
    total_pages = get_total_pages(get_gtml(url))
    for i in range(1, total_pages+1):
        url_gen = base_url + page_part + str(i) + query_part
        # print(url_gen)
        html = get_gtml(url_gen)
        get_page_data(html)

if __name__ == '__main__':
    main()
