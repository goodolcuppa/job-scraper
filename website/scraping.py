import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def reed_url(role, location):
    # create URL based on form input
    base_url = "https://www.reed.co.uk/jobs/"

    # format input as it would be in the URL
    formatted_role = '-'.join(str(role).lower().split(' '))
    formatted_location = '-'.join(str(location).lower().split(' '))

    # return the URL depending on which input was passed
    if formatted_role and formatted_location:
        return f"{base_url}{formatted_role}-jobs-in-{formatted_location}"
    elif formatted_role and not formatted_location:
        return f"{base_url}{formatted_role}-jobs"
    elif not formatted_role and formatted_location:
        return f"{base_url}jobs-in-{formatted_location}"
    else:
        return base_url
    
def parse_reed_salaries(series):
    value_list = series.split()

    # ignore salaries paid at an hourly or daily rate
    for value in value_list:
        if value.lower() in ['hour', 'hr', 'day']:
            return None
    
    # locate currency values and convert them
    values = [float(x.replace('£', '').replace(',', '')) for x in value_list if x[0] == '£']

    # return the values, average of values, or None,
    # depending on number of currency values found
    if len(values) == 1:
        return values[0]
    elif len(values) == 2:
        return (values[0] + values[1]) / 2
    else:
        return None

def scrape_reed_jobs(url):
    print(f'Scraping {url} ...')

    # get HTML response
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []

    # parse listings from response
    page_listings = soup.find_all('article')
    for listing in page_listings:
        item = {
            'title': ' '.join(listing.find('a', {'data-element': 'job_title'}).text.split()),
            'company': ' '.join(listing.find('a', class_='gtmJobListingPostedBy').text.split()),
            'url': 'https://www.reed.co.uk' + listing.find('a', {'data-element': 'job_title'}).attrs['href'],
            'location': ' '.join(listing.find('li', {'data-qa': 'job-card-location'}).text.split()),
            'salary': ' '.join(listing.find('svg', {'aria-labelledby': 'title-salary'}).parent.text.split())
        }
        items.append(item)

    # create a DataFrame of results
    df = pd.DataFrame(items)

    # # get job listings from sample data
    # df = pd.read_csv('website/data/reed_jobs.csv')

    return df

def parse_indeed_salaries(series):
    return None

def scrape_indeed_jobs(role, location):
    # create browser with URL
    url = 'https://uk.indeed.com'
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    delay = 1
    time.sleep(delay)

    # search by input if elements are present
    try:
        job_title_input = driver.find_element(By.ID, value='text-input-what')
        job_location_input = driver.find_element(By.ID, value='text-input-where')
        job_title_input.send_keys(role)
        job_location_input.send_keys(location)
        time.sleep(1)
        job_location_input.send_keys(Keys.ENTER)
    except TimeoutException:
        return

    # get HTML response from new page once loaded
    soup = None
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, 'mosaic-provider-jobcards'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
        return
    
    print(f'Scraping {driver.current_url} ...')

    # parse listings from response
    data = []
    if soup:
        page_listings = soup.find_all('td', class_='resultContent')
        for listing in page_listings:
            item = {
                'title': listing.find('h2', class_='jobTitle').text,
                'company': listing.find('span', {'data-testid': 'company-name'}).text,
                'url': url + listing.find('a', class_='jcs-JobTitle').attrs['href'],
                'location': listing.find('div', {'data-testid': 'text-location'}).text,
                'salary': 'Unknown'
            }
            data.append(item)
        
    # create a DataFrame of results
    df = pd.DataFrame(data)

    # # get job listings from sample data
    # df = pd.read_csv('website/data/indeed_jobs.csv')

    return df

def parse_glassdoor_salaries(series):
    value_list = series.split(' ')

    # ignore salaries paid at an hourly or daily rate
    for value in value_list:
        if value.lower() in ['hour', 'hr', 'day']:
            print('Paid at an hourly or daily rate. Ignoring value.')
            return None

    # locate currency values and convert them
    values = [x.replace('£', '') for x in value_list if x[0] == '£']
    values = [float(x[:-1]) * (1000 * (x[-1] == 'K')) for x in values]

    # return the values, average of values, or None,
    # depending on number of currency values found
    if len(values) == 1:
        return values[0]
    elif len(values) == 2:
        return (values[0] + values[1]) / 2
    else:
        return None

def scrape_glassdoor_jobs(role, location):
    # create browser with URL
    url = 'https://www.glassdoor.co.uk/Job/index.htm'
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    delay = 1
    time.sleep(delay)

    # search by input if elements are present
    try:
        job_title_input = driver.find_element(By.ID, value='searchBar-jobTitle')
        job_location_input = driver.find_element(By.ID, value='searchBar-location')
        job_title_input.send_keys(role)
        job_location_input.send_keys(location)
        time.sleep(1)
        job_location_input.send_keys(Keys.ENTER)
    except TimeoutException:
        return

    # get HTML response from new page once loaded
    soup = None
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jobCard'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
        return
    
    print(f'Scraping {driver.current_url} ...')

    # parse listings from response
    data = []
    if soup:
        page_listings = soup.find_all('div', class_='jobCard')
        for listing in page_listings:
            salary_div = listing.find('div', {'data-test': 'detailSalary'})
            
            item = {
                'title': listing.find('a', {'data-test': 'job-title'}).text,
                'company': listing.find('div').find('div').find('span').text,
                'url': listing.find('a', {'data-test': 'job-title'}).attrs['href'],
                'location': listing.find('div', {'data-test': 'emp-location'}).text,
                'salary': salary_div.text.replace(u'\xa0', u' ') if salary_div else 'Unknown'
            }
            data.append(item)

    # create a DataFrame of results
    df = pd.DataFrame(data)

    # # get job listings from sample data
    # df = pd.read_csv('website/data/glassdoor_jobs.csv')

    return df