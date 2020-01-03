#!/usr/bin/env python

import click

from modules.utils import logger
from tld import get_tld


@click.group()
def cli():
    pass


@click.command()
def all_chapters():
    from app import Scraper
    
    url = click.prompt("Novel URL")

    info = get_tld(url, as_object=True)

    scraper = Scraper(info.domain, url)

    logger.info("Scraping {} Chapter Started...".format(url))
    scraper.run()


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
cli.add_command(compile_chapters, name="compile")
cli.add_command(recompile)
cli.add_command(rename)
cli.add_command(update)


if __name__ == '__main__':
    cli()
