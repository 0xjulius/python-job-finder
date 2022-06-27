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
        print(f"Työtehtävän nimi: {company_name}")
        print(f"Sijainti: {location.strip()} {date.strip()}")
        print(f'Linkki: {url}')
        print(f'******************************************')
        print(f'')
       
       
url = "https://www.monster.fi/tyopaikat/it?search=&job_geo_location=Vaasa%2C+Suomi&radius=50&Etsi+ty%C3%B6paikkoja=Etsi+ty%C3%B6paikkoja&lat=63.09508899999999&lon=21.6164564&country=Suomi&administrative_area_level_1=undefined"
baseUrl = "https://monster.fi"
nimi = "Monster.fi"
print(f'')
html_text = requests.get(url).text
soup = BeautifulSoup(html_text, 'lxml')
jobs = soup.find_all('div', class_ = 'job__content clearfix')
available_jobs = soup.find('div', class_ = 'recruiter-seo-search-content-header')
results = available_jobs.find('h1', class_ = 'search-result-header').text
print(f'******************************************')
print(f"{nimi} - {results}")
print(f'Listataan työpaikat..')
print(f'')
for job in jobs:
        actual_name = job.find('span', class_ = 'recruiter-company-profile-job-organization').text
        company_name = job.find('h2', class_ = 'node__title').text
        date = job.find('span', class_ = 'date').text
        location = job.find('div', class_ ='location').text
        url = job.a['href']
        
        print(f"{nimi}")
        print(f"Työpaikan nimi: {actual_name.strip()}")
        print(f"Työtehtävän nimi: {company_name.strip()}")
        print(f"Sijainti: {location.strip()} {date.strip()}")
        print(f'Linkki: {url}')
        print(f'******************************************')
        print(f'')