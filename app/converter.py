import pypandoc
from halo import Halo
from slugify import slugify

from config import set_compiled_file, EPUB_CONVERTED_DIRECTORY, EPUB_FONTS_DIRECTORY


def convert(title):
    input_filename = set_compiled_file(title)
    output_filename = "{}/{}.epub".format(EPUB_CONVERTED_DIRECTORY, slugify(title))

    pandoc_args = ["--epub-embed-font={}".format(EPUB_FONTS_DIRECTORY), '--toc']

    spinner = Halo(text="Converting to Epub: Novel {}".format(title), text_color="red")
    spinner.start()

    output = pypandoc.convert_file(source_file=input_filename, to='epub', format='md',
                                   extra_args=pandoc_args,
                                   outputfile=output_filename)

    spinner.stop()
    spinner.succeed("Converting {} done.".format(title))
