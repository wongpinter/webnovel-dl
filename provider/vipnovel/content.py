import re
from bs4 import BeautifulSoup
from slugify import slugify


class Content:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup

    def __parse_chapter_title(self, soup):
        if soup is None:
            raise Exception("Page tidak dapat di scraping...")

        section = soup.find("div", {"class": "entry-content"})

        if section is None:
            raise Exception("Content tidak ditemukan..")

        title_on_content = section.find(lambda tag: (tag.name == "p" and
                                                  re.compile(r'[Cc]hapter\s.+\d+').search(tag.text)))

        title_on_tag = section.find(
            lambda tag: (tag.name == "h1" or tag.name == "h3" or tag.name == "h2" or tag.name == "h4"))

        title_in_breadcrumb = soup.find("ol", {'class': 'breadcrumb'}).find('li', {'class', 'active'}).text

        if title_on_content:
            title = self._fix_br_on_title(title_on_content)
        elif title_on_tag is not None:
            title = title_on_tag.text.strip()
        else:
            title = title_in_breadcrumb

        if title is None:
            return False

        title_text = title.strip()

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
    def __convert_br(el, soup):
        for br in el.find_all("br"):
            br.replace_with("\n\n");

    @staticmethod
    def _italic(el, soup):
        for italic in el.find_all("em"):
            the_text = italic.get_text()

            if italic.string:
                new_tag = soup.new_tag("em")
                new_tag.string = "*" + the_text + "*"

                italic.string.replace_with(new_tag)

    @staticmethod
    def _fix_br_on_title(title):
        if title.find("br") is not None:
            for br in title.find_all("br"):
                return br.previous_sibling.strip()

        return title.text.strip()

    @staticmethod
    def _fix_br_on_content_with_title(paragraph):
        if paragraph.find("br") is not None:
            for br in paragraph.find_all("br"):
                return br.next_sibling.strip()

        return paragraph.text.strip()

    def __parse_content_chapter(self, soup):
        content = soup.find('div', {'class': "reading-content"})

        page = ''
        for paragraph in content.find_all(lambda tag: (tag.name == "p")
                                                      and not re.compile(r'Translator[:\']').search(tag.text)
                                                      and not re.compile(r'Book\s+\d+\s+–').search(tag.text)):
            self._italic(paragraph, soup)

            if re.compile(r'[Cc]hapter\s+(\d+)\s?[–\-:]?').search(paragraph.text):
                parsed = self._fix_br_on_content_with_title(paragraph)
            else:
                parsed = paragraph.text

            self.__convert_br(paragraph, soup)

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
        current_page = soup.find('li', {'class': 'active'})

        if current_page:
            return slugify(current_page.text.strip(), to_lower=True)

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
