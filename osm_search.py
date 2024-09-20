import re
from collections.abc import Sequence
from itertools import chain

from rapidfuzz import fuzz, process
from sklearn.neighbors import BallTree

from config import (
    EARTH_RADIUS,
    OSM_SEARCH_RADIUS_0,
    OSM_SEARCH_RADIUS_1,
    OSM_SEARCH_RADIUS_NONAME,
    OSM_SEARCH_SCORE_THRESHOLD_1,
    OSM_SEARCH_SCORE_THRESHOLD_2,
)
from osm_poi import OsmPoi
from overpass import Overpass
from um_poi import UmPoi
from utils import beautify_name, radians_tuple


def _distance_score(distance: float) -> float:
    if distance < OSM_SEARCH_RADIUS_1:
        return 1

    if distance > OSM_SEARCH_RADIUS_0:
        return 0

    return (OSM_SEARCH_RADIUS_0 - distance) / (OSM_SEARCH_RADIUS_0 - OSM_SEARCH_RADIUS_1)


def _tags_score(all_tags: dict[str, str], subset_tags: dict[str, str]) -> float:
    if not subset_tags:
        return 0

    for k, v in subset_tags.items():
        if all_tags.get(k) != v:
            return 0

    return 1


def _get_names(tags: dict[str, str]) -> tuple[str, ...]:
    result = []

    for k, v in tags.items():
        if 'name' in k:
            result.append(v)

    if result:
        return tuple(result)
    else:
        return ('',)


def _normalize_name(name: str) -> str:
    name = beautify_name(name)

    if not name:
        return ''

    name = re.sub(r'[^\w\s]', ' ', name.lower())
    name = re.sub(r'\s+', ' ', name).strip()

    return name


class OsmSearch:
    def __init__(self) -> None:
        self.pois: list[OsmPoi] = []

        for e in Overpass().query_pois():
            if 'center' in e:
                e |= e['center']

            self.pois.append(
                OsmPoi(
                    type=e['type'],
                    id=e['id'],
                    tags=e['tags'],
                    lat=e['lat'],
                    lon=e['lon'],
                )
            )

        self.tree = BallTree(tuple(radians_tuple((p.lat, p.lon)) for p in self.pois), metric='haversine')

    def search(self, um_pois: Sequence[UmPoi], pass_: int) -> Sequence[OsmPoi | None]:
        if pass_ not in (1, 2):
            raise ValueError(f'Invalid pass: {pass_}')

        search_score_threshold = OSM_SEARCH_SCORE_THRESHOLD_1 if pass_ == 1 else OSM_SEARCH_SCORE_THRESHOLD_2

        if not um_pois:
            return ()

        indices, distances = self.tree.query_radius(
            tuple(radians_tuple((p.lat, p.lon)) for p in um_pois),
            r=OSM_SEARCH_RADIUS_0 / EARTH_RADIUS,
            return_distance=True,
            sort_results=True,
        )

        result = []

        for um_poi, i_distances, i_indices in zip(um_pois, distances, indices, strict=True):
            if len(i_indices) == 0:  # skip if no results
                continue

            um_poi_name = _normalize_name(um_poi.name)
            um_poi_noname = not um_poi_name
            um_poi_osm_tags = um_poi.get_osm_category_tags()

            osm_pois = tuple(self.pois[index] for index in i_indices)
            osm_pois_names_group = tuple(tuple(_normalize_name(name) for name in _get_names(p.tags)) for p in osm_pois)
            osm_pois_names_flat = tuple(chain.from_iterable(osm_pois_names_group))

            name_scores = process.extract(um_poi_name, osm_pois_names_flat, scorer=fuzz.partial_token_sort_ratio)
            name_scores_map = {name: score / 100 for name, score, _ in name_scores}

            matches = []

            for distance, osm_poi, osm_poi_names in zip(i_distances, osm_pois, osm_pois_names_group, strict=True):
                distance_meters = distance * EARTH_RADIUS
                best_match = None

                for name in osm_poi_names:
                    if um_poi_noname or not name:
                        distance_score = 1 if distance_meters < OSM_SEARCH_RADIUS_NONAME else 0
                        tags_score = _tags_score(osm_poi.tags, um_poi_osm_tags)
                        name_score = 1
                    else:
                        distance_score = _distance_score(distance_meters)
                        tags_score = 1
                        name_score = name_scores_map.get(name, 0)

                    score = distance_score * tags_score * name_score
                    if score < 0 or score > 1:
                        raise RuntimeError(f'Invalid score: {score} = {distance_score} * {tags_score} * {name_score}')

                    if best_match is None:
                        best_match = (-score, distance, osm_poi)
                    else:
                        best_match = min(best_match, (-score, distance, osm_poi))

                matches.append(best_match)

            matches.sort()
            best_match_score = -matches[0][0]
            best_match_osm_poi = matches[0][2]

            if best_match_score >= search_score_threshold:
                result.append(best_match_osm_poi)
            else:
                result.append(None)
                print(
                    f'✗ [{best_match_score:.3f}] {um_poi_name!r} ({um_poi.category!r}) ↔ {best_match_osm_poi.tags.get("name")!r}'
                )

        return tuple(result)
