import aiofiles
import aiohttp
import json

from provider import provider
from config import CHAPTERS_LIST_NAME, MAX_TCP
from modules.utils import retry, user_agent, logger


# from provider.wuxiaworld import Content as Parser


async def get_body(url):
    header = user_agent()
    connector = aiohttp.TCPConnector(limit=MAX_TCP, ttl_dns_cache=33600)

    async with aiohttp.ClientSession(connector=connector, headers=header) as session:
        try:
            return await fetch(session, url)
        except (
                aiohttp.ClientConnectionError
        ) as e:
            logger.debug(
                "aiohttp exception for %s [%s]: %s",
                url,
                getattr(e, "status", None),
                getattr(e, "message", None),
            )


@retry(aiohttp.ClientConnectionError, aiohttp.ClientError, aiohttp.ClientResponseError, verbose=False)
async def fetch(session, url):
    async with session.get(url, timeout=60) as response:
        return await response.read()


async def get_results(url, save_path):
    _temp = __import__("provider.{}".format(provider.provider_name), globals(), locals(), ['Content'])
    Parser = _temp.Content

    html = await get_body(url)

    parser = Parser(html)
    result = parser.get_results()

    await save(save_path, result)


async def save(path, content):
    filesave = "{}/{}".format(path, CHAPTERS_LIST_NAME)

    async with aiofiles.open(filesave, mode="+a") as writer:
        await writer.write(json.dumps(content) + "\r\n")
        await writer.flush()


async def handle_tasks(task_id, work_queue, progressbar, options):
    while not work_queue.empty():
        current_url = await work_queue.get()
        try:
            task_status = await get_results(current_url, options['save_path'])
            progressbar.update()
        except Exception as e:
            logger.exception('Error for {}'.format(
                current_url), exc_info=True)
        finally:
            work_queue.task_done()
