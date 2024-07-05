import pickle
import re
import time
from base64 import urlsafe_b64encode
from collections.abc import Generator
from contextlib import contextmanager
from hashlib import blake2b
from math import radians

import httpx

from config import CACHE_DIR, UNICODE_QUOTES, USER_AGENT


@contextmanager
def print_run_time(message: str | list) -> Generator[None, None, None]:
    print(f'[⏱️] {message}...')
    start_time = time.perf_counter()

    try:
        yield
    finally:
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        # support message by reference
        if isinstance(message, list):
            message = message[0]

        print(f'[⏱️] {message} took {elapsed_time:.3f}s')


def nice_hash(o: object) -> str:
    return (
        urlsafe_b64encode(
            blake2b(
                repr(o).encode(),
                digest_size=8,
                usedforsecurity=False,
            ).digest()
        )
        .decode()
        .rstrip('=')
    )


def file_cache(ttl: float):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            hash_args = nice_hash((args, kwargs))
            cache_file = CACHE_DIR / f'{func.__name__}.{hash_args}.pkl'

            if cache_file.is_file() and (time.time() - cache_file.stat().st_mtime) < ttl:
                with cache_file.open('rb') as f:
                    return pickle.load(f)  # noqa: S301

            result = func(*args, **kwargs)

            with cache_file.open('wb') as f:
                pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)

            return result

        return wrapped

    return wrapper


def radians_tuple(latlon: tuple[float, float]) -> tuple[float, float]:
    return (radians(latlon[0]), radians(latlon[1]))


def get_http_client(base_url: str = '', *, headers: dict | None = None) -> httpx.Client:
    if not headers:
        headers = {}

    return httpx.Client(
        base_url=base_url,
        headers={'User-Agent': USER_AGENT, **headers},
        timeout=30,
        follow_redirects=True,
        http1=True,
        http2=True,
    )


def beautify_name(name: str) -> str:
    if not name:
        return ''

    # capitalize first letter in all uppercase words
    for m in re.finditer(r'[^\d\W]+', name):
        word = m.group()

        if word.isupper():
            name = name[: m.start()] + word.capitalize() + name[m.end() :]

    # normalize unicode quotes
    name = ''.join(UNICODE_QUOTES.get(c, c) for c in name)

    # trim non-alphanumeric characters
    name = re.sub(r'^[^\w"\']+', '', name)
    name = re.sub(r'[^\w"\']+$', '', name)

    # fix inconsistent quotes
    if name.count('"') == 1 and name.count("'") == 1:
        name = name.replace("'", '"')

    # strip quotes
    while name and not name[0].isalnum() and not name[-1].isalnum():
        name = name[1:-1]

    # trim whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return name
