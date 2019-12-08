from glob import glob
from pathlib import Path
from tinydb import TinyDB
from slugify import slugify

from config import NOVEL_STORAGE_PATH, METADATA_NAME


def get_all_dir():
    for path in sorted(glob(NOVEL_STORAGE_PATH + "/*")):
        db = TinyDB("{}/{}".format(path, METADATA_NAME))
        metadata = db.get(doc_id=1)

        folder_name = Path(path).name

        new_path_dir = "{}/{}".format(NOVEL_STORAGE_PATH, slugify(folder_name, to_lower=True))

        metadata['directory_path'] = new_path_dir
        print(metadata['directory_path'])

        db.update(metadata)

        Path(path).rename(new_path_dir)
        # print(NOVEL_STORAGE_PATH, folder_name)
