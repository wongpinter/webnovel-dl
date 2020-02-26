from bs4 import BeautifulSoup

from config import DOMAIN_URL
from modules.utils import fetch, logger


class Chapters:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup
        self.chapters = []

    def get_chapter(self, url=None):
        if url is None:
            soup = self.soup
            self.soup = None
        else:
            soup = fetch(url)

        for li in soup.find_all("li", {"class": "wp-manga-chapter"}):
            self.chapters.append(li.find("a")['href'])

        return None

    def get_novel_name(self):
        title = self.soup.find('div', {"class": "post-title"}).find("h3")

        if title is None:
            raise Exception("Novel title not found")

        return title.text.strip()

    def all(self):
        novel_name = self.get_novel_name()
        self.get_chapter()

        logger.info("Total chapters for novel {}: {}".format(novel_name, len(self.chapters)))

    def get_all(self):
        return self.chapters

    def get_last(self):
        return self.chapters[-1]
