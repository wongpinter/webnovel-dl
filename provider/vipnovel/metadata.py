from bs4 import BeautifulSoup
import re


class Metadata:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup
        self.metadata = dict()

    def parse(self):
        self.metadata = self.summary()

        return self.metadata

    def summary(self):
        summary_content = self.soup.find("div", {"class", "summary_content"})

        title = self.soup.find("div", {"class", "post-title"}).find("h3").text.strip()

        image = self.soup.find("div", {'class', 'summary_image'}).find('img')['src']

        data = dict()
        for summary_heading in summary_content.find_all("div", {"class": "post-content_item"}):
            heading = summary_heading.find("div", {'class', 'summary-heading'})
            content = summary_heading.find('div', {'class', 'summary-content'})

            data[heading.text.strip()] = content.text.strip()

        description = self.soup.find("div", {"class": "summary__content"})

        synopsis = ''
        for paragraph in description.find_all(lambda tag: (tag.name == "p")
                                                          and not (re.compile(r'(COO|links)').search(tag.text)
                                                                   or (re.compile(r'VIPNOVEL').search(tag.text))
                                                                   or (
                                                                           re.compile(r'Description').search(
                                                                               tag.text)))):
            synopsis += paragraph.text.strip() + "\n\n"

        metadata = dict(
            title=title,
            image=image,
            author=[data['Author(s)']],
            genre=[x.strip() for x in data['Genre(s)'].split(',')],
            status=data['Status'],
            synopsis=synopsis.strip()
        )

        return metadata
