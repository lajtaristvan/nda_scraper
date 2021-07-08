import requests
import re
import random
import pandas as pd
from bs4 import BeautifulSoup
from math import ceil
from tqdm import tqdm
from user_agents import user_agent_list


class NdaScraper():

    def __init__(self, url):
        self.url = url        


    def scraper(self):
        # This is a session
        s = requests.Session()

        # Make a request in a session
        r = s.get(self.url)

        # Scrape the content to end page
        soup = BeautifulSoup(r.content, 'lxml')

        # Scrape the end page number
        try:
            end_page_number = int(soup.find_all('p', class_='form-control-static')[1].text.strip()[18:])
        except:
            end_page_number = 'no end page'

        # Scrape the sum page number
        try:
            sum_page_number = int(soup.find_all('p', class_='form-control-static')[1].text.strip()[12:-7])
        except:
            sum_page_number = 'no sum page number'

        # Define the end page number
        try:
            end_page = ceil((end_page_number / sum_page_number) + 1)
        except:
            end_page = 0  

        # A list to productlinks
        productlinks = []

        # Iterate all productlinks between a range
        for x in range(1, end_page):

            # Make a request in a session                  
            r = s.get(self.url + f'?page={x}')

            # Scrape the content
            soup = BeautifulSoup(r.content, 'lxml')

            # Identify all products
            productlist = soup.find_all('p', class_='text-center')

            # Save all links in productlinks list
            for item in productlist:
                for link in item.find_all('a', href=True):
                    productlinks.append(link['href'])
                    #print(link['href'])

        # A list to the scraping data
        list = []

        # Iterate all links in productlinks
        for link in tqdm(productlinks):
            # Pick a random user agent
            user_agent = random.choice(user_agent_list.user_agent_list)

            # Set the headers
            headers = {
                'User-Agent': user_agent
            }

            # Make requests with headers in one sessions (s)
            r = s.get(link, headers=headers)

            # Scrape the content in the soup variable with 'lxml' parser
            soup = BeautifulSoup(r.content, 'lxml')  

            # Scrape name
            try:
                name = str(soup.title.string.strip()[:-10])
            except:
                name = ''

            # Scrape barcode
            try:
                barcode = str(soup.select('tr:nth-child(2) > td:nth-child(2)')[0].string.strip())                
            except:
                barcode = ''

            # Scrape pack size
            try:
                pack_size = int(soup.find(text=re.compile("Pack Size:")).strip()[11:])
            except:
                pack_size = 1

            # Scrape netto unit price and origi price
            try:
                netto_unit_price_origi_price = float(soup.find_all('span', class_='highlight', limit=1)[0].string.strip()[1:])            
            except:
                netto_unit_price_origi_price = float()            

            # Scraper gross unit price and origi price
            try:
                gross_unit_price_origi_price = float(soup.find_all('span', class_='highlight')[0].next_sibling.string.strip()[10:])                      
            except:
                gross_unit_price_origi_price = float()

            # VAT calculation    
            if gross_unit_price_origi_price == 0:
                gross_unit_price_origi_price = netto_unit_price_origi_price      

            vat = round(((gross_unit_price_origi_price - netto_unit_price_origi_price) / netto_unit_price_origi_price) * 100)            

            # Scrape product code
            try:                
                product_code = str(soup.select('tr:nth-child(1) > td:nth-child(2)')[0].string.strip())
            except:
                product_code = ''

            # Scrape availability            
            try:
                availability = bool(soup.select('span.text-success.highlight > strong')[0].string.strip())                
            except:
                availability = bool(False)

            # Define a dictionary for csv
            nda = {                   
                'link': link,
                'name': name,
                'barcode': barcode,
                'pack_size': pack_size,
                'netto_unit_price_origi_price': netto_unit_price_origi_price,
                'gross_unit_price_origi_price': gross_unit_price_origi_price,
                'vat': vat,                
                'product_code': product_code,        
                'availability': availability
            }

            # Add the dictionary to the list every iteration
            list.append(nda)

            # Print every iteration        
            # print(
            #     '\n--------- Saving: ---------\n'             
            #     'link: ' + str(nda['link']) + '\n'
            #     'name: ' + str(nda['name']) + '\n'
            #     'barcode: ' + str(nda['barcode']) + '\n'
            #     'pack size: ' + str(nda['pack_size']) + '\n'
            #     'netto unit price origi price: ' + str(nda['netto_unit_price_origi_price']) + '\n'
            #     'gross unit price origi price: ' + str(nda['gross_unit_price_origi_price']) + '\n'
            #     'vat: ' + str(nda['vat']) + '\n'             
            #     'product code: ' + str(nda['product_code']) + '\n'
            #     'availability: ' + str(nda['availability']) + '\n'
            # )

        # Make table to list
        df = pd.DataFrame(list)

        # Save to csv        
        df.to_csv(r'C:\WEBDEV\nda_scraper\exports\nda.csv', mode='a', index=False, header=True)        


get_nda_arts_and_crafts = NdaScraper('https://www.nda-toys.com/16/arts-and-crafts-wholesale')
get_nda_books = NdaScraper('https://www.nda-toys.com/14/books-wholesale')
get_nda_party_supplies = NdaScraper('https://www.nda-toys.com/372/party-supplies-wholesale')
get_nda_stationery = NdaScraper('https://www.nda-toys.com/15/stationery-wholesale')
get_nda_toys = NdaScraper('https://www.nda-toys.com/13/toys-wholesale')

get_nda_arts_and_crafts.scraper()
get_nda_books.scraper()
get_nda_party_supplies.scraper()
get_nda_stationery.scraper()
get_nda_toys.scraper()