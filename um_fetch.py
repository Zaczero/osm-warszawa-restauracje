from itertools import chain
from typing import Sequence

import hjson
from pyproj import Transformer
from rapidfuzz import fuzz, process, utils
from tenacity import retry, stop_after_attempt, wait_exponential

from config import UM_CATEGORY_TAGS, UM_GUESS_CATEGORY, UM_VALID_CATEGORIES
from um_poi import UmPoi
from utils import get_http_client, nice_hash

_GUESS_CATEGORY_CHOICES = tuple(chain(UM_GUESS_CATEGORY, UM_VALID_CATEGORIES))
_PROJ_TRANSFORMER = Transformer.from_crs('epsg:2178', 'wgs84')


@retry(wait=wait_exponential(), stop=stop_after_attempt(8))
def _fetch_data(theme: str) -> list[dict]:
    with get_http_client() as http:
        r = http.post('https://mapa.um.warszawa.pl/mapviewer/foi', data={
            'request': 'getfoi',
            'version': '1.0',
            'bbox': '0:0:10000000:10000000',
            'width': '760',
            'height': '1190',
            'theme': theme,
            'cachefoi': 'yes',
        })
        r.raise_for_status()

    result = hjson.loads(r.text)['foiarray']
    assert result, 'No data returned'
    return result


def _parse_details(details: str) -> tuple[str, str, str]:
    kv_map = {}

    for line in details.split('\n'):
        parts = line.split(':', maxsplit=1)
        key = parts[0].strip()
        value = parts[1].strip()
        kv_map[key] = value

    return kv_map['Rodzaj punktu'], kv_map['Nazwa punktu'], kv_map['Adres']


def _guess_category(name: str) -> str:
    matches = process.extract(name, _GUESS_CATEGORY_CHOICES,
                              scorer=fuzz.partial_ratio,
                              processor=utils.default_process,
                              limit=3,
                              score_cutoff=85)

    if not matches:
        return ''

    if len(matches) == 1:
        match = matches[0][0]
    else:
        match = max(matches, key=lambda m: len(UM_CATEGORY_TAGS[UM_GUESS_CATEGORY.get(m[0], m[0])]))[0]

    return UM_GUESS_CATEGORY.get(match, match)


def um_fetch_restaurants() -> Sequence[UmPoi]:
    data = _fetch_data('dane_wawa.ZEZWOLENIA_ALKOHOLOWE_GASTRO')
    data_a = _fetch_data('dane_wawa.ZEZWOLENIA_ALKOHOLOWE_GASTRO_A')
    foiarray = chain(data, data_a)

    pois: dict[str, UmPoi] = {}

    for p in foiarray:
        lat, lng = _PROJ_TRANSFORMER.transform(p['y'], p['x'])
        um_category, name, address = _parse_details(p['name'])

        category = _guess_category(name)

        if category:
            print(f'🧩 Guessed category {category!r} for {name!r}')
        if not category:
            category = um_category
            print(f'🏱 Using UM category {category!r} for {name!r}')

        p_id = nice_hash((name, address))

        pois[p_id] = UmPoi(
            id=p_id,
            id_um=p['id'],
            category=category,
            name=name,
            address=address,
            lat=lat,
            lng=lng)

    return tuple(pois.values())
