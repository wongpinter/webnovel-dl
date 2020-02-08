import re
from bs4 import BeautifulSoup
from slugify import slugify

from config import DOMAIN_URL


class Content:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup

    @staticmethod
    def __parse_chapter_title(soup):
        if soup is None:
            raise Exception("Page tidak dapat di scraping...")

        section = soup.find("div", {"id": "chapter-content"})

        if section is None:
            raise Exception("Content tidak ditemukan..")

        title_in_content = section.find(
            lambda tag: (tag.name == "p" and re.search(r'^[Cc]hapter:?\s+\d+', tag.text)) or (tag.name == "h3"))

        if title_in_content is None:
            raw_title = soup.find(
                'li', {'class': 'active'}).find_next('a')['title']
        else:
            raw_title = title_in_content.text

        if raw_title is None:
            return False

        title_text = raw_title.strip()

        title_text = re.sub(r"\b(\d+)\s?-\s?(\1)\b", r'\1 - ', title_text)
        title_text = re.sub(r"–", "-", title_text)
        title_text = re.sub(r"’", "'", title_text)
        title_text = re.sub(r":", " - ", title_text)
        title_text = re.sub(r"(\d+)\.", "\\1 - ", title_text)
        title_text = re.sub(r"(Chapter \d+)\s+", "\\1 - ", title_text)
        title_text = re.sub(r"-\s-", "-", title_text)
        title_text = re.sub(r"\s\s+", " ", title_text)

        return title_text

    @staticmethod
    def __get_active_url(soup):
        active_url = soup.find(
            'li', {'class': 'active'}).find_next('a')['href']

        return "{}{}".format(DOMAIN_URL, active_url)

    @staticmethod
    def _italic(el, soup):
        for italic in el.find_all("em"):
            the_text = italic.get_text()

            if italic.string:
                new_tag = soup.new_tag("em")
                new_tag.string = "*" + the_text + "*"

                italic.string.replace_with(new_tag)

    def __parse_content_chapter(self, soup):
        content = soup.find('div', {'id': "chapter-content"})

        page = ''
        for paragraph in content.find_all(lambda tag: (tag.name == "p")
                                          and not re.compile(r'[Cc]hapter\s+(\d+)\s?[–\-:]?').search(
                tag.text)
                and not re.compile(r'Translator[:\']').search(tag.text)
                and not re.compile(r'Book\s+\d+\s+–').search(tag.text)):
            self._italic(paragraph, soup)

            parsed = paragraph.text.strip()
            parsed = re.sub(r'^…$', '', parsed)
            parsed = re.sub(r'^-{3,}$', '-', parsed)
            parsed = re.sub(r'^\.{3,}$', '..', parsed)
            parsed = re.sub(r'\[', '*', parsed)
            parsed = re.sub(r'\]', '*', parsed)

            parsed = re.sub(r'「', '*「', parsed)
            parsed = re.sub(r'」', '」*', parsed)
            parsed = re.sub(r'『', '*『', parsed)
            parsed = re.sub(r'』', '』*', parsed)
            parsed = re.sub(r'^~+$', '-', parsed)

            parsed = re.sub(r'＜＜', '*', parsed)
            parsed = re.sub(r'＞＞', '*', parsed)
            parsed = re.sub(r"[\t]*", "", parsed)

            page += parsed.strip() + "\n\n"

            page = re.sub(r"[\t]*", "", page)

        return page.strip()

    @staticmethod
    def __parse_next_chapter(soup):
        next_page = soup.find('a', {'id': "next_chap"})

        if next_page.has_attr('href'):
            return slugify(next_page['href'], to_lower=True)

        return None

    @staticmethod
    def __parse_previous_chapter(soup):
        previous_page = soup.find('a', {'id': "prev_chap"})

        if previous_page.has_attr('href'):
            return slugify(previous_page['href'], to_lower=True)

        return None

    @staticmethod
    def __parse_current_chapter(soup):
        current_page = soup.find('li', {'class': 'active'}).find_next('a')

        if current_page.has_attr('href'):
            return slugify(current_page['href'], to_lower=True)

        return None

    def get_results(self):
        soup = self.soup
        page = dict(
            title=self.__parse_chapter_title(soup),
            slug=self.__parse_current_chapter(soup),
            url=self.__get_active_url(soup),
            next_chapter=self.__parse_next_chapter(soup),
            previous_chapter=self.__parse_previous_chapter(soup),
            content=self.__parse_content_chapter(soup)
        )

        return page
