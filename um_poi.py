from typing import NamedTuple

from config import UM_CATEGORY_TAGS


class UmPoi(NamedTuple):
    id: str
    id_um: str
    category: str
    name: str
    address: str
    lat: float
    lon: float

    def get_osm_category_tags(self) -> dict[str, str]:
        try:
            return UM_CATEGORY_TAGS[self.category]
        except KeyError:
            print(f'❓ Unknown category {self.category!r} for {self.name!r}')
            return UM_CATEGORY_TAGS['']
