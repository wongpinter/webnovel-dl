import re
from bs4 import BeautifulSoup
from slugify import slugify


class Content:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup

    @staticmethod
    def __parse_chapter_title(soup):
        if soup is None:
            raise Exception("Page tidak dapat di scraping...")

        section = soup.find("div", {"class": "reading-content"})

        if section is None:
            raise Exception("Content tidak ditemukan..")

        title_in_content = section.find(
            lambda tag: (tag.name == "p" and re.search(r'^[Cc]hapter:?\s+\d+', tag.text)) or (tag.name == "h3"))

        title_in_breadcrumb = soup.find("ol", {'class': 'breadcrumb'}).find('li', {'class', 'active'}).text

        title_in_header = soup.find('div', {'class': 'cha-tit'})

        if title_in_header is not None:
            raw_title = title_in_header.find_next('h3').text
        elif title_in_content is not None:
            raw_title = title_in_content.text
        else:
            raw_title = title_in_breadcrumb

        if raw_title is None:
            return False

        title_text = raw_title.strip()

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
            'meta', {'property': 'og:url'})['content']

        return active_url

    @staticmethod
    def _italic(el, soup):
        for italic in el.find_all("em"):
            the_text = italic.get_text()

            if italic.string:
                new_tag = soup.new_tag("em")
                new_tag.string = "*" + the_text + "*"

                italic.string.replace_with(new_tag)

    def __parse_content_chapter(self, soup):
        content = soup.find('div', {'class': "reading-content"})

        page = ''
        for paragraph in content.find_all(lambda tag: (tag.name == "p")
                                                      and not re.compile(r'[Cc]hapter\s+(\d+)\s?[–\-:]?').search(
            tag.text)
                                                      and not re.compile(r'Translator[:\']').search(tag.text)
                                                      and not re.compile(r'Book\s+\d+\s+–').search(tag.text)):
            self._italic(paragraph, soup)

            for br in paragraph.find_all("br"):
                br.replace_with("\n\n")

            parsed = paragraph.text
            parsed = re.sub(r'^…$', '', parsed)
            parsed = re.sub(r'^-{3,}$', '-', parsed)
            parsed = re.sub(r'^\.{3,}$', '..', parsed)
            parsed = re.sub(r'\[', '**_', parsed)
            parsed = re.sub(r'\]', '_**', parsed)

            parsed = re.sub(r'「', '*「', parsed)
            parsed = re.sub(r'」', '」*', parsed)
            parsed = re.sub(r'『', '*『', parsed)
            parsed = re.sub(r'』', '』*', parsed)

            parsed = re.sub(r'＜＜', '**', parsed)
            parsed = re.sub(r'＞＞', '**', parsed)

            page += parsed + "\n\n"

        return page.strip()

    @staticmethod
    def __parse_next_chapter(soup):
        next_page = soup.find('a', {'class': "next_page"})

        if next_page is not None:
            if next_page.has_attr('href'):
                return slugify(next_page['href'], to_lower=True)

        return None

    @staticmethod
    def __parse_previous_chapter(soup):
        previous_page = soup.find('a', {'class': "prev_page"})

        if previous_page is not None:
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
            slug=slugify(self.__get_active_url(soup), to_lower=True),
            url=self.__get_active_url(soup),
            next_chapter=self.__parse_next_chapter(soup),
            previous_chapter=self.__parse_previous_chapter(soup),
            content=self.__parse_content_chapter(soup)
        )

        return page
