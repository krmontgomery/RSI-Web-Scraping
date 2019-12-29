from bs4 import BeautifulSoup
from selenium import webdriver
import time
import urllib3
import requests
import csv

http = urllib3.PoolManager()

csv_file = open('122819_SC_Ships_Available.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file, )
csv_writer.writerow(['Ship', 'Ship Price','Ship Image', 'Link to Ship'])

shipURLs = requests.get('https://robertsspaceindustries.com/pledge/ships').text

def findShipURL():
    # Note the driver path may be different on your PC
    browser = webdriver.Chrome(r'C:\Users\User\Desktop\chromedriver_win32 78\chromedriver.exe')
    browser.get("https://robertsspaceindustries.com/pledge/ships")

    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
    source_data = browser.page_source
    soup = BeautifulSoup(source_data, 'lxml')
    for url in soup.find_all('a', class_='filet'):
        if url.has_attr('href'):
            data = []
            data.append(f"""https://robertsspaceindustries.com{url['href']}""")
            yield '\n'.join(data)    

generator = findShipURL()
for item in generator:
    data = []    
    data.append(item)
    url = item
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'lxml')
    for shipName in soup.find_all('div', class_='buying-options-content'):
        data = []
        shipName = soup.find('div',class_='type').text
        final_price = soup.find('div', class_='price').text
        if final_price.endswith('USD'):
            final_price = final_price[:-4]
        shipFName = shipName.split('\n')[1]
        shipFName = shipFName.strip()
        shipLName = shipName.split('\n')[2]
        shipLName = shipLName.strip()
        data.append(f"""\nShip: {shipFName} {shipLName} \nShip Price: {final_price}""")
        for image in soup.find_all('span', class_='thumbnails clearfix'):
            findImageURLString = image.findChildren()[4]['href'] 
            buildImageURL = f'https://robertsspaceindustries.com{findImageURLString}'  
            if findImageURLString.startswith('/'):
                sheetLink = f'''=IMAGE('https://robertsspaceindustries.com{findImageURLString}')'''
            else: 
                sheetLink = f'''=IMAGE('{findImageURLString}')'''
            data.append(f"""Ship URL: {url} \nImage: {buildImageURL}""")
            # print('\n'.join(data))
        csv_writer.writerow([shipFName + shipLName ,final_price, sheetLink,url])
csv_file.close()


# -------------------- Finding the Description for Each Ship -----------------------
# source = requests.get('https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-Hornet').text
# soup = BeautifulSoup(source, 'lxml')

# ----------> Find a better way to grab description
# description = soup.find('div', class_='excerpt')
# data = []
# print(f'{description.text.strip()}')

# ----------> Format in Google Sheets for images if I wanted to intergrate pricture of ships???
# ----------> Problem with wrapping dynamic variable with double quotes. Looking for solution...
# =IMAGE(“https://robertsspaceindustries.com/media/3e0oc9s85451kr/store_slideshow_large/F7c_hornet_front-Right_visual.jpg", 1, 50, 25)
