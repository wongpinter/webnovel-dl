import asyncio
import tqdm

from config import CHAPTERS_LIST_NAME
from modules.utils import logger, total_chapters, remove as remove_file


def compile_novel(title):
    from app import Compiler

    compiler = Compiler(title=title)
    compiler.run()


def convert_novel(title):
    from app import convert

    convert(title)


class Producer:
    def __init__(self, urls, handle_tasks, max_threads, options=None):
        self.loop = asyncio.new_event_loop()
        self.urls = urls
        self.handle_tasks = handle_tasks
        self.max_threads = max_threads
        self.options = options

    def run(self):
        queue = asyncio.Queue()
        [queue.put_nowait(url) for url in self.urls]

        logger.info("Total chapters proccessing {}".format(queue.qsize()))

        self.options['total'] = queue.qsize()

        remove_file("{}/{}".format(self.options["save_path"], CHAPTERS_LIST_NAME))

        progressbar = tqdm.tqdm(
            desc="Scraping Proggress", total=queue.qsize(), position=0, leave=False, unit='chapter'
        )

        asyncio.set_event_loop(self.loop)
        tasks = [self.handle_tasks(task_id, queue, progressbar, self.options) for task_id in range(self.max_threads)]

        try:
            self.loop.run_until_complete(asyncio.wait(tasks))
        finally:
            self.loop.close()
            progressbar.clear()
            logger.info("Scraping Done.")

        total_chapters(self.options['total'], self.options['save_path'])

        compile_novel(self.options['title'])
