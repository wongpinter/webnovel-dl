def total_chapters(total_chapter: int, chapters_file) -> bool:
    import json
    from modules.utils import logger

    from config import CHAPTERS_LIST_NAME

    chapters = [json.loads(line) for line in open("{}/{}".format(chapters_file, CHAPTERS_LIST_NAME))]

    total_chapter_downloaded = len(chapters)

    if int(total_chapter) > total_chapter_downloaded:
        logger.info("Total downloaded chapters {} less than total chapters {}".format(total_chapter, len(chapters)))

    logger.info("Total Chapters: {}, Total Chapter Downloaded {}".format(total_chapter, len(chapters)))

def json_valid(json_data: str) -> bool:
    import json

    try:
        json.load(json_data)
        return True
    except json.JSONDecodeError:
        return False