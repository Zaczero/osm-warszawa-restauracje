from collections.abc import Iterable

import xmltodict

from config import CHANGESET_ID_PLACEHOLDER, CREATED_BY, DEFAULT_POI_TAGS
from um_poi import UmPoi
from utils import beautify_name


def _initialize_osm_change_structure() -> dict:
    return {
        'osmChange': {
            '@version': 0.6,
            '@generator': CREATED_BY,
            'create': {
                'node': [],
            },
        }
    }


def create_pois(pois: Iterable[UmPoi]) -> str:
    result = _initialize_osm_change_structure()
    create_nodes: list = result['osmChange']['create']['node']

    for i, p in enumerate(pois, 1):
        create_node = {
            '@id': -i,
            '@changeset': CHANGESET_ID_PLACEHOLDER,
            '@version': 1,
            '@lat': p.lat,
            '@lon': p.lon,
            'tag': [
                {
                    '@k': k,
                    '@v': v,
                }
                for k, v in (DEFAULT_POI_TAGS | p.get_osm_category_tags()).items()
            ],
        }

        if name := beautify_name(p.name):
            create_node['tag'].append({'@k': 'name', '@v': name})

        create_nodes.append(create_node)

    return xmltodict.unparse(result)
