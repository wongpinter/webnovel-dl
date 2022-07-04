#!/usr/bin/env python

from distutils.log import info
import click
from app import scraper

from modules.utils import logger
from tld import get_tld


@click.group()
def cli():
    pass


@cli.command()
@click.argument('filename', type=click.File('r'))
def download_from_file(filename):
    from app import Scraper

    for line in filename.readlines():
        url = line.strip()
        if url:
            info = get_tld(url, as_object=True)
            scraper = Scraper(info.domain, url)
            logger.info("Downloading {}".format(url))
            scraper.run()


@click.command()
@click.option("--url", default=None, help="novel url to scrape")
def all_chapters(url):
    from app import Scraper

    if url is None:
        url = click.prompt("Novel URL")

    info = get_tld(url, as_object=True)

    scraper = Scraper(info.domain, url)

    logger.info("Scraping {} Chapter Started...".format(url))
    scraper.run()


@click.command()
@click.argument('filename', type=click.Path(exists=True))
def batch(filename):
    """Print FILENAME if the file exists."""
    logger.info("Opening file list {}".format(click.format_filename(filename)))
    with open(click.format_filename(filename)) as f:
        urls = f.read().splitlines()

    from app import Scraper
    logger.info("Attempted to scraping {} novels".format(len(urls)))

    novel = 0
    for url in urls:
        novel = novel + 1
        info = get_tld(url, as_object=True)
        scraper = Scraper(info.domain, url)

        logger.info("Queue {} from {} Novel. {} for all chapter started...".format(novel, len(urls), url))
        scraper.run()

    logger.info("Batch Scraping done.")


@click.command()
@click.argument("title")
def compile_chapters(title):
    from app import Compiler

    compiler = Compiler(title)

    logger.info("Scraping {} Chapter Started...".format(title))
    compiler.run()


@click.command()
def recompile():
    from app import Compiler
    import time

    with open("lists.txt", 'r') as reader:
        for line in reader:
            title = line.strip()
            compiler = Compiler(title)

            logger.info("Recompile {} Chapters Started...".format(title))
            compiler.run()
            time.sleep(0.2)


@click.command()
@click.argument("title")
def update(title):
    from app import UpdateChapter

    updater = UpdateChapter(title)
    updater.run()


@click.command()
def rename():
    from app.rename import get_all_dir

    get_all_dir()


cli.add_command(all_chapters)
cli.add_command(download_from_file)
cli.add_command(batch)
cli.add_command(compile_chapters, name="compile")
cli.add_command(recompile)
cli.add_command(rename)
cli.add_command(update)

if __name__ == '__main__':
    cli()
