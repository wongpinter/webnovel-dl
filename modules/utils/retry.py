import logging
import asyncio

from functools import wraps

log = logging.getLogger(__name__)


def retry(*exceptions, retries=3, cooldown=2, verbose=True):
    """Decorate an async function to execute it a few times before giving up.
    Hopes that problem is resolved by another side shortly.

    Args:
        exceptions (Tuple[Exception]) : The exceptions expected during function execution
        retries (int): Number of retries of function execution.
        cooldown (int): Seconds to wait before retry.
        verbose (bool): Specifies if we should log about not successful attempts.
    """

    def wrap(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            retries_count = 0

            while True:
                try:
                    result = await func(*args, **kwargs)
                except exceptions as err:
                    retries_count += 1
                    message = "Exception during {} execution. " \
                              "{} of {} retries attempted".format(func, retries_count, retries)

                    if retries_count > retries:
                        verbose and log.exception(message)
                        raise Exception(
                            func.__qualname__, args, kwargs) from err
                    else:
                        verbose and log.warning(message)

                    if cooldown:
                        await asyncio.sleep(cooldown)
                else:
                    return result

        return inner

    return wrap
