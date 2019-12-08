import os
from slugify import slugify
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.curdir)
load_dotenv(dotenv_path="{}/.env".format(ROOT_DIR))

DOMAIN_URL = os.getenv("DOMAIN_URL")
MAX_THREAD = int(os.getenv("MAX_THREAD"))
NOVEL_STORAGE_PATH = os.getenv("NOVEL_STORAGE_PATH")
METADATA_NAME = os.getenv("METADATA_NAME")
CHAPTERS_LIST_NAME = os.getenv("CHAPTERS_LIST_NAME")
CHAPTERS_COMPILED_NAME = os.getenv("CHAPTERS_COMPILED_NAME")

EPUB_STYLESHEET_NAME = os.getenv("EPUB_STYLESHEET_NAME")
EPUB_FONTS = os.getenv("EPUB_FONTS")
EPUB_STYLESHEET_PATH = "{}/{}".format(ROOT_DIR, EPUB_STYLESHEET_NAME)
EPUB_FONTS_DIRECTORY = "{}/{}".format(ROOT_DIR, EPUB_FONTS)

EPUB_CONVERTED_DIRECTORY = os.getenv("EPUB_CONVERTED_DIRECTORY")


def set_metadata_file(title):
    title = slugify(title, to_lower=True)
    return "{}/{}/{}".format(NOVEL_STORAGE_PATH, title, METADATA_NAME)


def set_chapter_lists_file(title):
    title = slugify(title, to_lower=True)
    return "{}/{}/{}".format(NOVEL_STORAGE_PATH, title, CHAPTERS_LIST_NAME)


def set_compiled_file(title):
    title = slugify(title, to_lower=True)
    return "{}/{}/{}".format(NOVEL_STORAGE_PATH, title, CHAPTERS_COMPILED_NAME)


def get_metadata_folder(title):
    title = slugify(title, to_lower=True)
    return os.path.dirname(set_metadata_file(title))


def get_compiled_file_folder(title):
    title = slugify(title, to_lower=True)
    return os.path.dirname(set_compiled_file(title))
