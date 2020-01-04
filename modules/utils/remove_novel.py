import shutil
import os

from config import get_metadata_folder
from modules.utils import logger


def remove_folder(title):
    folder_path = get_metadata_folder(title)

    if os.path.exists(folder_path):
        logger.info("Deleting Folder {}".format(folder_path))
        shutil.rmtree(folder_path)
