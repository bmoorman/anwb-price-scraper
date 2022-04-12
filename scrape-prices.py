#!/usr/bin/env python3

import time
import json
from datetime import datetime
from influxdb import InfluxDBClient
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

URL = 'https://energie.anwb.nl/actuele-tarieven'
    
def scrape_prices(URL):

    client = InfluxDBClient(host='10.0.0.4', port=8086)
    client.switch_database('anwb')
        
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-dev-shm-usage') # Not used 
      
    driver = webdriver.Chrome(options=options)
    time.sleep(5)
    driver.get(URL)
    
    time.sleep(7)
    date = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelector('.date')")
    button = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelectorAll('.arrow-container')[1]")
    webdriver.ActionChains(driver).move_to_element(button).perform()
    webdriver.ActionChains(driver).click().perform()
    date = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelector('.date')")
    print(date.text);
    tomorrow = datetime.strptime(date.text, '%d %B %Y')
#    print(tomorrow.date())
    canvas = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelector('canvas')")
    webdriver.ActionChains(driver).move_to_element(canvas).perform()
    webdriver.ActionChains(driver).move_by_offset(8, 100).perform()
    tooltip = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelector('#chartjs-tooltip')")
#    print(tooltip.get_attribute('innerHTML'));
    webdriver.ActionChains(driver).move_by_offset(-319, 0).perform()
    webdriver.ActionChains(driver).click().perform()
    tooltip = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelector('#chartjs-tooltip')")
    for t in range(24):
        tooltip = driver.execute_script("return document.querySelector('ez-app').shadowRoot.querySelector('current-prices').shadowRoot.querySelector('flex-rates-component').shadowRoot.querySelector('#chartjs-tooltip')")
        html = tooltip.get_attribute('innerHTML')
        soup = BeautifulSoup(html, "html.parser")
        str = soup.get_text()
     #   print(str)
        timestamp = f'{tomorrow.date()}t{str[0:2]}:00:00z'
     #   tomorrow.replace(hour=t)
      #  print(tomorrow.time())
        price = [
            {
                'measurement': 'anwb-kwh-hourly',
                'time': timestamp,
                'fields': {
                    'price': float(str[15:19].replace(',', '.'))
                }
            }
        ]
        client.write_points(price)
        print (json.dumps(price))
        webdriver.ActionChains(driver).move_by_offset(29, 0).perform()  
        webdriver.ActionChains(driver).click().perform()        
        
    client.close();
    src = driver.page_source
    driver.close()

    return src

if __name__ == '__main__':
    scrape_prices(URL)
