from bs4 import BeautifulSoup
from halo import Halo

from modules.utils import fetch

DOMAIN_URL = "https://allnovelfull.com"

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

        for ul in soup.find_all("ul", {"class": "list-chapter"}):
            for a in ul.find_all("a"):
                if a:
                    self.chapters.append("{}{}".format(DOMAIN_URL, a['href']))

        for pagination in soup.find_all("ul", {"class": "pagination pagination-sm"}):
            next_page = pagination.find("li", {"class": "next"}).find('a')
            break
        
        if pagination is None:
            raise Exception("pagination not found")

        next_page = pagination.find("li", {"class": "next"}).find('a')

        if next_page:
            return "{}{}".format(DOMAIN_URL, next_page['href'])

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
