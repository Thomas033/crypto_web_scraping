from operator import ge
from matplotlib.pyplot import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os

def create_driver():
    '''
    Create driver from url "https://finance.yahoo.com/topic/crypto/"
    and accept cookies
    '''
    url = 'https://finance.yahoo.com/topic/crypto/'
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--start-fullscreen')
    chrome_options.add_argument('--single-process')

    # Set path to chromedriver as per your configuration
    homedir = os.path.expanduser("~")
    webdriver_service = Service(f"{homedir}/chromedriver/stable/chromedriver")

    # Choose Chrome Browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.implicitly_wait(10)

    driver.get(url)

    driver.find_element(By.XPATH, '//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[1]').click()

    #html_page = driver.page_source.encode("utf-8")

    return driver

def get_basic_info(driver):
    articles = driver.find_elements(By.CLASS_NAME, 'Ov\(h\).Pend\(44px\).Pstart\(25px\)')
    titles = []
    summaries = []
    sources = []
    for article in articles:
        titles.append(article.find_element(By.TAG_NAME, "a").text)
        summaries.append(article.find_element(By.TAG_NAME, "p").text)
        sources.append(article.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    df = pd.DataFrame.from_dict({
        'TITLE':titles,
        'SUMMARY':summaries,
        'SOURCE':sources
        })

    return df


if __name__ == "__main__":
    driver = create_driver()
    df  = get_basic_info(driver)
    print(df)
