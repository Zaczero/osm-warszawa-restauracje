from typing import Sequence

from config import OVERPASS_API_INTERPRETER
from utils import get_http_client


def build_pois_query(timeout: int) -> str:
    return (
        f'[out:json][timeout:{timeout}];'
        'relation(id:336075);'  # https://www.openstreetmap.org/relation/336075
        'map_to_area;'
        'nwr[!highway][name](area);'
        'out tags center qt;'
    )


class Overpass:
    def __init__(self) -> None:
        self.http = get_http_client(OVERPASS_API_INTERPRETER)

    def query_pois(self) -> Sequence[dict]:
        timeout = 90
        query = build_pois_query(timeout)

        r = self.http.post('', data={'data': query}, timeout=timeout * 2)
        r.raise_for_status()

        elements = r.json()['elements']

        return tuple(elements)
