import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()
scraper = cloudscraper.create_scraper()


def user_agent():
    return {
        "USER-AGENT": ua.chrome
    }


def fetch(url):
    page = scraper.get(url, headers=user_agent())

    return BeautifulSoup(page.content, "lxml")