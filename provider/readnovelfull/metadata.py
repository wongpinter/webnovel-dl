import slugify
from bs4 import BeautifulSoup


class Metadata:
    def __init__(self, soup):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'lxml')

        self.soup = soup
        self.metadata = dict()

    def parse(self):
        self.metadata = self.get_novel_attributes()
        self.metadata['title'] = self.get_novel_name()
        self.metadata['slug'] = slugify.slugify(self.metadata['title'], to_lower=True)
        self.metadata['synopsis'] = self.get_novel_synopsis()

        return self.metadata

    def get_novel_attributes(self):
        info = self.soup.find("ul", {"class": "info info-meta"})

        if info is None:
            raise Exception("Information for novel not found..")

        section_author = info.find_next('li').find_next("li")
        section_genre = section_author.find_next('li')
        section_source = section_genre.find_next('li')
        section_status = section_source.find_next('li')

        attributes = dict(
            author=[],
            genre=[],
            status=[]
        )

        for author in section_author.find_all('a'):
            if author is not None:
                attributes["author"].append(author.text)

        for genre in section_genre.find_all('a'):
            if genre is not None:
                attributes["genre"].append(genre.text)

        for status in section_status.find_all('a'):
            if status is not None:
                attributes["status"] = status.text

        image = self.soup.find(
            'div', {'class': 'book'}).find_next('img')['src']

        attributes['image'] = "{}{}".format("", image)

        return attributes


    def get_novel_name(self):
        title = self.soup.find('h3', {"class": "title"})

        if title is None:
            raise Exception("Novel title not found")

        return title.text.strip()

    def get_novel_synopsis(self):
        description = self.soup.find('div', {"class": "desc-text"})

        if description is None:
            raise Exception("Novel does not have synopsis")

        synopsis = ''
        for paragraph in description.find_all(lambda tag: (tag.name == "p")):
            synopsis += paragraph.text.strip() + "\n\n"

        return synopsis.strip()
