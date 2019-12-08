import asyncio
import aiohttp
import time
import async_timeout
from bs4 import BeautifulSoup
from halo import Halo

from modules.utils import logger
from config import set_chapter_lists_file
from provider.novelfull import Content as Parser
from database import Metadata


def compile_novel(title):
    from app import Compiler

    compiler = Compiler(title=title)
    compiler.run()


class UpdateChapter:
    def __init__(self, title=None):
        self.metadata = Metadata(slug=title)
        self.loop = asyncio.get_event_loop()
        self.new_chapters = []

    async def main(self):
        last_chapter = self.metadata.last_chapter()
        await remove_last_line(set_chapter_lists_file(self.metadata.slug()))

        title = self.metadata.title()

        spinner = Halo(text="Updating for last chapters: Novel {}".format(title), text_color="green")
        spinner.start()

        while True:
            last_chapter = await self.get_last_chapter(last_chapter)

            if last_chapter is None:
                break

            last_chapter = "http://novelfull.com{}".format(last_chapter)
            self.new_chapters.append(last_chapter)

        spinner.stop()
        spinner.succeed("Updating {} done. {} new chapters added".format(title, len(self.new_chapters)))

    async def get_last_chapter(self, last_chapter):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, last_chapter)
            next_last_chapter = await self.get_next_chapter(html)
            return next_last_chapter

    @staticmethod
    async def fetch(session, url):
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()

    def update_metadata(self):
        if len(self.new_chapters) > 0:
            self.metadata.update_chapters(self.new_chapters)
        else:
            logger.info("No new chapters found")

    async def get_next_chapter(self, html):
        soup = BeautifulSoup(html, 'lxml')

        await self.save_chapter(soup)

        next_page = soup.find('a', {'id': "next_chap"})

        if next_page.has_attr('href'):
            return next_page['href']

    async def save_chapter(self, soup):
        import aiofiles
        import json

        parser = Parser(soup)
        content = parser.get_results()

        filesave = set_chapter_lists_file(self.metadata.slug())

        async with aiofiles.open(filesave, mode="+a") as writer:
            await writer.write(json.dumps(content) + "\r\n")
            await writer.flush()

    def run(self):
        logger.info("Updating {} starting...".format(self.metadata.title()))
        self.loop = asyncio.get_event_loop()

        try:
            self.loop.run_until_complete(self.main())
        finally:
            self.update_metadata()

        logger.info("Updating done..")
        time.sleep(1)


async def remove_last_line(filename):
    import os

    with open(filename, "r+", encoding="utf-8") as file:

        # Move the pointer (similar to a cursor in a text editor) to the end of the file
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1
        file.seek(pos, os.SEEK_SET)
        if file.readline() == "\n":
            pos = file.tell() - 3
            file.seek(pos, os.SEEK_SET)

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()
