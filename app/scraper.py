from config import get_metadata_folder, MAX_THREAD
from modules.utils import fetch, logger
from modules.worker import Producer as Worker, handle_tasks
from database import Metadata as MetadataDB
from provider.novelfull import Metadata as MetadataParser, Chapters as ChapterParser


class Scraper:
    def __init__(self, url: str = None):
        self.url = url
        self.soup = fetch(self.url)
        self.novel = dict()
        self.db = None

        self.metadata()

    def metadata(self):
        metadata = MetadataParser(self.soup)
        print(metadata)
        self.novel = metadata.parse()
        self.novel['directory_path'] = get_metadata_folder(self.novel['title'])
        self.novel['url'] = self.url

        self.init_db()

    def init_db(self):
        self.db = MetadataDB(self.novel['title'])

    def chapters_from_scraper(self):
        chapter = ChapterParser(self.soup)
        chapter.all()

        return chapter.get_all()

    def save(self, chapters):
        self.novel["chapters"] = chapters
        self.novel["total_chapters"] = len(chapters)
        self.db.save(self.novel)

        logger.info("Metadata novel {} successfully saved at {}"
                    .format(self.novel['title'], self.novel['directory_path']))

    def all_chapters(self):
        chapters = self.db.all_chapters()

        if chapters is None:
            chapters = self.chapters_from_scraper()

        self.save(chapters)

        return chapters

    def run(self):
        worker = Worker(self.all_chapters(), handle_tasks, MAX_THREAD,
                        options={"save_path": self.novel["directory_path"], "title": self.novel['title']})
        worker.run()
