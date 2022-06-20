from ast import With
from bs4 import BeautifulSoup
import requests
import time

    
url = "https://duunitori.fi/tyopaikat?alue=vaasa&haku=it&order_by=date_posted"
baseUrl = "https://duunitori.fi"
nimi = "Duunitori.fi"
print(f'')
html_text = requests.get(url).text
soup = BeautifulSoup(html_text, 'lxml')
jobs = soup.find_all('div', class_ = 'grid grid--middle job-box job-box--lg')
for job in jobs:
        company_name = job.find('h3', class_ = 'job-box__title').text
        date = job.find('span', class_ = 'job-box__job-posted').text
        location = job.find('span', class_ ='job-box__job-location').text
        url = baseUrl+job.a['href']
        
        print(f"{nimi}")
        print(f"Työpaikan nimi: {company_name}")
        print(f"Sijainti: {location.strip()} {date.strip()}")
        print(f'Linkki: {url}')
        print(f'******************************************')
        print(f'')
       