import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm

from config import CHAPTERS_LIST_NAME
from provider import provider
from modules.utils import logger, total_chapters, remove as remove_file, user_agent, fetch


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


class NewProducer:
    def __init__(self, urls, options):
        self.urls = urls
        self.options = options

    def run(self):
        # with ThreadPoolExecutor(3) as executor:
        #     executor.map(lambda f: get_results(*f), (self.urls, self.options["save_path"]))

        with tqdm.tqdm(total=len(self.urls)) as pbar:
        # let's give it some more threads:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(get_results, arg, self.options["save_path"]): arg for arg in self.urls}
                results = {}
                for future in as_completed(futures):
                    arg = futures[future]
                    results[arg] = future.result()
                    pbar.update(1)

        logger.info("Scraping Done.")

        total_chapters(len(self.urls), self.options['save_path'])

        compile_novel(self.options['title'])



def get_results(url, save_path):
    _temp = __import__("provider.{}".format(provider.provider_name), globals(), locals(), ['Content'])
    Parser = _temp.Content

    html = get_body(url)

    parser = Parser(html)
    result = parser.get_results()

    save(save_path, result)

    return True


def save(path, content):
    filesave = "{}/{}".format(path, "chapters.json")

    with open(filesave, mode="+a") as writer:
        writer.write(json.dumps(content) + "\r\n")
        writer.flush()


def get_body(url):
    header = user_agent()
    try:
        return fetch(url)
    except:
        logger.debug("exception for %s", url)
