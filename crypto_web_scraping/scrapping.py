import requests
from bs4 import BeautifulSoup
import pandas as pd

def create_soup(url="https://finance.yahoo.com/topic/crypto/"):
    '''
    Create soup for crypto article from yahoo by default.
    Accept all url
    '''
    response = requests.get(url)
    if response.status_code != 200:
        return print(f"Error: unable to request the url, status_code = {response.status_code}")
    return BeautifulSoup(response.content, "html.parser")

def get_basic_info(soup):
    '''
    Function to extract basic information from soup
    '''
    articles = soup.find_all("div", {"class":"Ov(h) Pend(44px) Pstart(25px)"})

    titles = []
    summaries = []
    sources = []
    urls = []
    BASIC_URL = "https://finance.yahoo.com/"

    for article in articles:
        titles.append(article.find("a").text)
        summaries.append(article.find("p").text)
        sources.append(article.find("div", {"class":"C(#959595) Fz(11px) D(ib) Mb(6px)"}).text)
        urls.append(BASIC_URL + article.find("a")["href"])

    df = pd.DataFrame({"TITLE":titles, "SUMMARIES":summaries, "SOURCES":sources, "LINK":urls})

    return df
