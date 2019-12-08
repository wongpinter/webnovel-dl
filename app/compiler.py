import os
import yaml
import json

from pprint import pprint

from config import set_compiled_file, set_chapter_lists_file, get_compiled_file_folder
from modules.utils import create_directory, download as download_cover, logger
from database import Metadata as MetadataDB


def convert_novel(title):
    from app import convert

    convert(title)


class Compiler:
    def __init__(self, title):
        self.metadata = MetadataDB(title)
        self.compiled_filename = set_compiled_file(title)
        self.chapters_filename = set_chapter_lists_file(title)
        self.chapters_sorted = []

        try:
            self.ordered_chapters()
        except ValueError as err:
            print(err)
            exit()

    def build_metadata(self):
        self.save(yaml_content=self.metadata.metadata_file())

    def download_cover(self):
        directory_save = "{}/{}".format(get_compiled_file_folder(title=self.metadata.title()), "raw.jpg")

        logger.info("Download cover for {}".format(self.metadata.title()))

        download_cover(self.metadata.cover_url(), directory_save)

    def build_chapter_contents(self):
        for chapter in self.chapters_sorted:
            content = "\n\n# {}\n\n\n{}".format(chapter['title'], chapter['content'])

            self.save(content=content)

    def save(self, content=None, yaml_content=None):
        with open(self.compiled_filename, "+a") as writer:
            if content is not None:
                writer.write(content)
            elif yaml_content is not None:
                yaml.dump(yaml_content, writer, allow_unicode=True,
                          explicit_start=True, explicit_end=True, default_flow_style=False,
                          sort_keys=False)

    def delete_compiled_file(self):
        if os.path.isfile(self.compiled_filename):
            os.remove(self.compiled_filename)
        else:
            logger.info("%s file not found created now.." % self.compiled_filename)
            create_directory(self.compiled_filename, with_filename=True)

    def ordered_chapters(self):
        chapters = [json.loads(line) for line in open(self.chapters_filename)]

        first_chapter = next((item for item in chapters if item["previous_chapter"] is None), False)

        if first_chapter is False:
            first_url = self.metadata.first_chapter()

            first_chapter = next((item for item in chapters if item["url"] == first_url), False)

            if first_chapter is False:
                raise ValueError("First Chapter is not found..")

        self.chapters_sorted.append(first_chapter)

        next_chapter = first_chapter['next_chapter']
        while True:
            # print(next_chapter)
            chapter = next((item for item in chapters if item["slug"] == next_chapter), None)

            # if chapter is None:
                # print(chapter)
                # break

            self.chapters_sorted.append(chapter)
            # print(chapter['next_chapter'])
            next_chapter = chapter['next_chapter']

            if next_chapter is None:
                break

    def save_ordered_chapters(self):
        os.remove(self.chapters_filename)

        for chapter in self.chapters_sorted:
            with open(self.chapters_filename, '+a') as writer:
                writer.write(json.dumps(chapter) + "\r\n")

    def run(self):
        logger.info("Compile {}".format(self.compiled_filename))
        self.delete_compiled_file()
        self.build_metadata()
        self.download_cover()
        self.save_ordered_chapters()
        self.build_chapter_contents()

        convert_novel(self.metadata.title())
