from collections.abc import Iterable

import polars as pl
from polars._typing import SchemaDict

from config import DB_PATH
from um_poi import UmPoi

_SCHEMA: SchemaDict = {
    'id': pl.Utf8,
    'id_um': pl.Utf8,
    'category': pl.Utf8,
    'name': pl.Utf8,
    'address': pl.Utf8,
    'lat': pl.Float64,
    'lon': pl.Float64,
    'reason': pl.Utf8,
}


def filter_added(pois: Iterable[UmPoi]) -> list[UmPoi]:
    existing_ids = set(
        pl.read_parquet(DB_PATH, columns=['id'], schema=_SCHEMA)
        .get_column('id')
        .to_list()
        if DB_PATH.is_file()
        else ()
    )
    return [poi for poi in pois if poi.id not in existing_ids]


def mark_added(pois: Iterable[UmPoi], reason: str | None = None) -> None:
    reason_dict = {'reason': reason} if reason else {}
    rows = [poi._asdict() | reason_dict for poi in pois]

    (
        (
            pl.read_parquet(DB_PATH, schema=_SCHEMA)
            if DB_PATH.is_file()
            else pl.DataFrame(None, _SCHEMA)
        )
        .vstack(pl.DataFrame(rows, _SCHEMA))
        .write_parquet(
            DB_PATH,
            compression='uncompressed',  # using disk compression
        )
    )
