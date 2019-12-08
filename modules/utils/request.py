import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


def user_agent():
    return {
        "USER-AGENT": ua.chrome
    }


def fetch(url):
    page = requests.get(url, headers=user_agent())

    return BeautifulSoup(page.content, "lxml")