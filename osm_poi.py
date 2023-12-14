from typing import NamedTuple


class OsmPoi(NamedTuple):
    type: str
    id: int
    tags: dict[str, str]
    lat: float
    lon: float
