from bs4 import BeautifulSoup
from halo import Halo

from modules.utils import fetch

DOMAIN_URL = "https://readnovelfull.com"

class Chapters:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup
        self.chapters = []
        self.base_chapter_url = "https://readnovelfull.com/ajax/chapter-archive?novelId="

    def get_chapter(self, url=None):
        if url is None:
            soup = self.soup
        
        novelId = soup.find("div", {"id": "rating"})['data-novel-id']

        if novelId is None:
            return

        s = fetch(f"{self.base_chapter_url}{novelId}")
        if s is None:
            return

        for a in s.find_all("a"):
            if a:
                self.chapters.append(f"{DOMAIN_URL}{a['href']}")

        return None

    def get_novel_name(self):
        title = self.soup.find('h3', {"class": "title"})

        if title is None:
            raise Exception("Novel title not found")

        return title.text.strip()

    def all(self):
        stop = False
        chapter_url = None

        novel_name = self.get_novel_name()

        spinner = Halo(text="Get all chapters.. Novel {}".format(novel_name), text_color="red")
        spinner.start()
        while not stop:
            chapter_url = self.get_chapter(url=chapter_url)
            if chapter_url is None:
                stop = True
                spinner.stop()
                spinner.succeed("Total chapters for novel {}: {}".format(novel_name, len(self.chapters)))

    def get_all(self):
        return self.chapters

    def get_last(self):
        return self.chapters[-1]