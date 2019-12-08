from tinydb import TinyDB
from slugify import slugify

from config import set_metadata_file, DOMAIN_URL, EPUB_STYLESHEET_PATH, set_compiled_file
from modules.utils import exists as file_exists, create_directory, logger
from datetime import datetime


class Metadata:
    def __init__(self, title=None, slug=None):
        if title:
            self.novel = dict(
                title=title,
                slug=slugify(title, to_lower=True),
                created_at=f'{datetime.now():%Y-%m-%d %H:%M:%S%z}'
            )
        elif slug:
            title = slug

        self.db_path = set_metadata_file(title)
        self.init()

    def exists(self):
        return file_exists(self.db_path)

    def init(self):
        if not self.exists():
            create_directory(self.db_path, with_filename=True)

        db = TinyDB(self.db_path)
        metadata = db.get(doc_id=1)

        if metadata is None:
            try:
                db.insert(self.novel)
            except TypeError as err:
                logger.info("Cannot save data.. {}".format(self.novel))
        else:
            self.novel = metadata

    def title(self):
        return self.novel['title']

    def slug(self):
        return self.novel['slug']

    def cover_url(self):
        # return self.novel['image']
        return "{}{}".format(DOMAIN_URL, self.novel['image'])

    def all_chapters(self):
        if "chapters" in self.novel:
            return self.novel["chapters"]

        return None

    def first_chapter(self):
        chapters = self.all_chapters()
        if chapters is not None:
            return chapters[0]

        return None

    def last_chapter(self):
        chapters = self.all_chapters()
        if chapters is not None:
            return chapters[-1]

        return None

    def update_chapters(self, last_chapters):
        for new_chapter in last_chapters:
            self.novel['chapters'].append(new_chapter)

        self.novel['total_chapters'] = len(self.novel['chapters'])
        logger.info("Saving {} new chapters".format(len(last_chapters)))

        self.save(self.novel)

    def metadata_file(self):
        from datetime import date

        compiled_folder = create_directory(set_compiled_file(self.novel['title']), with_filename=True)

        return {
            "title": [{
                "type": "main",
                "text": self.novel['title']
            }],
            "creator": [{
                "role": "author",
                "text": ", ".join(self.novel['author'])
            }],
            "subject": ", ".join(self.novel['genre']),
            "date": date.today(),
            "description": self.novel['synopsis'],
            "stylesheet": EPUB_STYLESHEET_PATH,
            "cover-image": "{}/cover.jpg".format(compiled_folder)
        }

    def save(self, data):
        data['updated_at'] = f'{datetime.now():%Y-%m-%d %H:%M:%S%z}'

        db = TinyDB(self.db_path)
        db.update(data)
