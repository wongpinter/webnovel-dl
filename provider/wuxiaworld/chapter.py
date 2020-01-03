from bs4 import BeautifulSoup
from natsort import natsorted

from modules.utils import logger


class Chapters:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup
        self.chapters = []

    def get_novel_name(self):
        title = self.soup.find("div", {"class", "post-title"}).text.strip()

        if title is None:
            raise Exception("Novel title not found")

        return title

    def all(self):
        list_content = self.soup.find("div", {'class': 'page-content-listing'})

        novel_name = self.get_novel_name()

        logger.info("Getting all chapters for {}".format(novel_name))
        for chapter in list_content.find_all("a"):
            self.chapters.append(chapter['href'])

    def get_all(self):
        return natsorted(self.chapters)
