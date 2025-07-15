import asyncio
import multiprocessing
from functools import reduce
from typing import Callable, Coroutine


def safe_get(collection, key, default=None):
    try:
        return collection.get(key, default)
    except (TypeError, AttributeError):
        pass

    try:
        return collection[key]
    except (IndexError, TypeError):
        pass

    try:
        return getattr(collection, key)
    except (AttributeError, TypeError):
        pass

    return default


def dig(collection, *keys, default=None, return_default_if_none=False):
    result = reduce(lambda x, y: safe_get(x, y, default), keys, collection)

    if result is None and default is not None and return_default_if_none:
        return default

    return result


def run_parallel(func: Callable, params: list[dict]):
    processes = []
    for param in params:
        process = multiprocessing.Process(
            target=func,
            kwargs=param,
        )
        processes.append(process)

    for process in processes:
        process.start()
    for process in processes:
        process.join()


def run_via_asyncio(coroutine: Coroutine):
    try:
        loop = asyncio.get_running_loop()
        return asyncio.create_task(coroutine)
    except RuntimeError:
        asyncio.run(coroutine)
