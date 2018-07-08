import requests
from bs4 import BeautifulSoup
import csv
import codecs
import pandas as pd
from selenium import webdriver
from time import sleep
import base64
from PIL import Image
import pytesseract



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

def pandas_open(file):
    df = pd.read_csv(file)
    return df.ix[:, 3].tolist()


class Bot:
    def __init__(self, data):
        self.data = data
        self.driver = webdriver.Firefox()
        self.navigate()


    def take_screenshot(self):
        self.driver.save_screenshot('avito_scr.png')


    def navigate(self):
        self.names = []
        self.numbers  = []
        self.df = pd.DataFrame()
        for i in self.data:
            try:
                self.driver.get(i)
                try:
                    name = self.driver.find_element_by_xpath('//div[@class="seller-info-name"]/a').text
                    self.names.append(name)
                except:
                    name = 'Не указано'
                    self.names.append(name)
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
                self.numbers.append(result)
                with open("result.txt", "a") as fil:
                    fil.write(result + ',')

            except Exception as e:
               result = 'Empty'
               self.numbers.append(result)
               with open("result.txt", "a") as fil:
                   fil.write(result + ',')
        self.df['names'] =  self.names
        self.df['numbers'] = self.numbers
        self.driver.quit()
        return self.df


def concat():
    df1 = pd.read_csv('avito.csv')
    df2 = Bot(pandas_open('avito.csv')).navigate()
    df = pd.DataFrame.concat([df1, df2], axis=1)
    return df.to_csv('avito_full', sep='\t', encoding='utf-8')


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
    concat()

if __name__ == '__main__':
    main()
