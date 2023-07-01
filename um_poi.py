from typing import NamedTuple

from config import UM_CATEGORY_TAGS


class UmPoi(NamedTuple):
    id: str
    category: str
    name: str
    address: str
    lat: float
    lng: float

    def get_osm_tags(self) -> dict[str, str]:
        return UM_CATEGORY_TAGS[self.category]
