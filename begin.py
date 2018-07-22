import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from time import sleep
import base64
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'


class Parse:
    def __init__(self, url):
        self.url = url

    @property
    def get_html(self):
        #берет урл, возвращает html
        r = requests.get(self.url)
        self.text = r.text
        return self.text
#         return r.text

    def get_total_pages(self):
        #берет html, возвращает количество страниц
        soup = BeautifulSoup(self.get_html, 'lxml')
        global total_pages
        try:
            pages = soup.find('div', class_ = 'pagination-pages').find_all('a', class_ = 'pagination-page')[-1].get('href')
            total_pages = pages.split('=')[1].split('&')[0]
        except Exception as e:
            total_pages = 1

        return int(total_pages)

    def get_page_data(self):
        #берет html, возвращает словарь с данными
        soup = BeautifulSoup(self.get_html, 'lxml')
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
            self.data = {'title':title,
                    'price':price,
                    'metro': metro,
                    'url': url}

            yield self.data

def write_csv(row):
    with open('C:\\Users\\USER\\Documents\\Python_Scripts\\avito\\scr\\avito.csv', 'a', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow((row['title'], row['price'], row['metro'],
                         row['url'], row['name'], row['phone_number']))

class Bot:
    def __init__(self, data):
        self.data = data


    def webdriver(self):
        self.driver = webdriver.Firefox()
        self.navigate()
        self.driver.quit()


    @property
    def get_urls(self):
        self.urls = [self.data[x]['url'] for x in range(len(self.data))]
        return self.urls


    def take_screenshot(self):
        self.driver.save_screenshot('avito_scr.png')

    def navigate(self):
        iter = 0
        for pos in self.get_urls:
            try:
                self.driver.get(pos)
                try:
                    name = self.driver.find_element_by_xpath('//div[@class="seller-info-name"]/a').text
                except:
                    name = 'Не указано'
                print(name)
                try:
                    button = self.driver.find_element_by_xpath('//a[@class="button item-phone-button js-item-phone-button button-origin button-origin-blue button-origin_full-width button-origin_large-extra item-phone-button_hide-phone item-phone-button_card js-item-phone-button_card"]')
                    button.click()

                    sleep(2)
                    self.take_screenshot()
                    image = self.driver.find_element_by_xpath('//div[@class="item-phone-big-number js-item-phone-big-number"]/img')
                    image_src = image.get_attribute('src').split(',')[1]
                    img = base64.decodebytes(bytearray(image_src, 'utf-8'))
                    with open("imageToSave.png", "wb") as f:
                        f.write(img)
                    image = Image.open('imageToSave.png')
                    result = pytesseract.image_to_string(image)
                except Exception as e:
                    print(str(e))

                print(result)
                self.data[iter]['name'] = name
                self.data[iter]['phone_number'] = result
                print(self.data[iter])
                write_csv(self.data[iter])
                iter = iter + 1
            except Exception as e:
                print(str(e))
                pass



def main():
    url = 'https://www.avito.ru/moskva?s_trg=3&q=%D0%B2%D1%8F%D0%BB%D0%B5%D0%BD%D0%B0%D1%8F+%D1%80%D1%8B%D0%B1%D0%B0'
    total_pages  = Parse(url).get_total_pages()
    print('total_pages ready')
    page_data = list(Parse(url).get_page_data())
    print('page_data ready')
#     url_list = Bot(page_data).get_urls()
#     print('url_list ready')
    driver = Bot(page_data).webdriver()
    print(driver)
#     result = Bot(url_list).navigate()
#     print(result)
#     base_url = 'https://www.avito.ru/sankt-peterburg/produkty_pitaniya?'
#     page_part = 'p='
#     query_part = '&user=1&q=%D1%80%D1%8B%D0%B1%D0%B0'
#     for i in range(1, total_pages+1):
#         url_gen = base_url + page_part + str(i) + query_part
#         page_data = Parse(url_gen).get_page_data()
if __name__ == '__main__':
    main()
