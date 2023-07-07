from typing import Iterable, Sequence

from tinydb import Query

from config import DB
from um_poi import UmPoi


def _is_added(poi: UmPoi) -> bool:
    entry = Query()
    return DB.contains(entry.id == poi.id)


def filter_added(pois: Iterable[UmPoi]) -> Sequence[UmPoi]:
    return tuple(filter(lambda poi: not _is_added(poi), pois))


def mark_added(pois: Iterable[UmPoi], reason: str = '') -> Sequence[int]:
    if reason:
        return DB.insert_multiple(poi._asdict() | {'reason': reason} for poi in pois)
    else:
        return DB.insert_multiple(poi._asdict() for poi in pois)
