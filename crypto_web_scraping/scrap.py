from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import time

def create_driver(url='https://finance.yahoo.com/topic/crypto/'):
    '''
    Create driver
    By default url =  "https://finance.yahoo.com/topic/crypto/"
    '''
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

    return driver

def get_basic_info(driver, export=True):
    '''
    From 'https://finance.yahoo.com/topic/crypto/' get basic information
    '''
    # Accept Cookies
    driver.find_element(By.XPATH, '//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[1]').click()
    driver.implicitly_wait(15)


    # Scroll down to get 20 articles

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    SCROLL_PAUSE_TIME = 0.5

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Scrap articles
    articles = driver.find_elements(By.CLASS_NAME, 'Ov\(h\).Pend\(44px\).Pstart\(25px\)')
    titles = []
    summaries = []
    sources = []
    links = []
    for article in articles:
        titles.append(article.find_element(By.TAG_NAME, "a").text)
        summaries.append(article.find_element(By.TAG_NAME, "p").text)
        sources.append(article.find_element(By.TAG_NAME, "span").text)
        links.append(article.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    # Create df to be returned
    df = pd.DataFrame.from_dict({
        'TITLE':titles,
        'SUMMARY':summaries,
        'SOURCE':sources,
        'LINK':links
        })

    if export == True:
        today = pd.Timestamp.today()
        df.to_csv(f"../raw_data/{today}", index=False)

    return df

def get_full_info(df):
    '''
    Df from get_basic_info() extract urls
    Get date, full text (if available, )
    '''

    df = df.copy()
    dates = []
    full_texts = []
    external_link = []
    cryptos = []

    urls = df["LINK"].to_list()

    for id, url in enumerate(urls):
        driver = create_driver(url)

        # Accept cookies
        driver.find_element(By.XPATH, '//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[1]').click()
        driver.implicitly_wait(5)
        try:
            # Find button for external sources (i.e no full text available)
            driver.find_element(By.XPATH, '//article/div/div/div[2]/a')
            external_link.append(1)
        except:
            try:
                driver.find_element(By.XPATH, '//article/div/div/div/div/div/div[2]/div[3]/div[2]/button').click()
                external_link.append(0)
            except:
                external_link.append(0)

        try:
            currencies = driver.find_elements(By.CLASS_NAME, "xray-card-content")
            dico = {}
            for currency in currencies:
                name = currency.find_element(By.CLASS_NAME, "xray-entity-title-link").text
                var = currency.find_element(By.CLASS_NAME, "xray-fin-streamer").text
                dico[name] = var
            cryptos.append(dico)
        except:
            cryptos.append("General")

        dates.append(driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime'))
        full_texts.append(driver.find_element(By.CLASS_NAME, "caas-body").text)
        print(f"article {id+1} done")

        driver.close()

    df["DATE"] = dates
    df["FULL_TEXT"] = full_texts
    df["CRYPTOS"] = cryptos
    df["EXTERNAL"] = external_link

    return df

if __name__ == "__main__":
    print("Creating driver")
    driver = create_driver()
    print("Gathering basic info")
    df = get_basic_info(driver)
    print("Getting full info")
    df = get_full_info(df)
    print(df)
