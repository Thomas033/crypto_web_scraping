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

def get_basic_info(driver):
    '''
    From 'https://finance.yahoo.com/topic/crypto/' get basic informations
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

    return df

def get_more_info(driver):
    '''
    From 'https://finance.yahoo.com/topic/crypto/' get basic informations
    '''

    # Accept Cookies
    driver.find_element(By.XPATH, '//*[@id="consent-page"]/div/div/div/form/div[2]/div[2]/button[1]').click()
    driver.implicitly_wait(15)


    # Scroll down to get 20 articles

    # # Get scroll height
    # last_height = driver.execute_script("return document.body.scrollHeight")

    # SCROLL_PAUSE_TIME = 0.5

    # while True:
    #     # Scroll down to bottom
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    #     # Wait to load page
    #     time.sleep(SCROLL_PAUSE_TIME)

    #     # Calculate new scroll height and compare with last scroll height
    #     new_height = driver.execute_script("return document.body.scrollHeight")
    #     if new_height == last_height:
    #         break
    #     last_height = new_height

    # Scrap articles
    articles = driver.find_elements(By.CLASS_NAME, 'Ov\(h\).Pend\(44px\).Pstart\(25px\)')
    titles = []
    summaries = []
    sources = []
    links = []
    dates = []
    full_texts = []
    for article in articles:
        titles.append(article.find_element(By.TAG_NAME, "a").text)
        summaries.append(article.find_element(By.TAG_NAME, "p").text)
        sources.append(article.find_element(By.TAG_NAME, "span").text)
        links.append(article.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    for id, title in enumerate(titles):
        article = driver.find_element(By.LINK_TEXT, title).click()
        print(f"article {id} OK")
        try:
            driver.find_element(By.XPATH, '//article/div/div/div/div/div/div[2]/div[3]/div[2]/button').click()
        except:
            pass

        dates.append(driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime'))
        full_texts.append(driver.find_element(By.CLASS_NAME, "caas-body").text)
        driver.back()
        driver.implicitly_wait(5)

    driver.quit()

    # Create df to be returned
    df = pd.DataFrame.from_dict({
        'TITLE':titles,
        'SUMMARY':summaries,
        'SOURCE':sources,
        'LINK':links,
        'DATE':dates,
        'FULL_TEXT':full_texts
        })

    return df



if __name__ == "__main__":
    driver = create_driver()
    df = get_basic_info(driver)
    df = append_full_info(df)
    print(df)
