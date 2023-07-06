import re
from collections import defaultdict
from typing import Sequence

from rapidfuzz import fuzz, process
from sklearn.neighbors import BallTree

from config import (EARTH_RADIUS, OSM_SEARCH_RADIUS_0, OSM_SEARCH_RADIUS_1,
                    OSM_SEARCH_RADIUS_NONAME, OSM_SEARCH_SCORE_THRESHOLD_1,
                    OSM_SEARCH_SCORE_THRESHOLD_2)
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


def _normalize_name(name: str) -> str:
    name = beautify_name(name)

    if not name:
        return ''

    name = re.sub(r'[^\w\s]', ' ', name.lower())
    name = re.sub(r'\s+', ' ', name).strip()

    return name


class OsmSearch:
    def __init__(self) -> None:
        self.pois = []

        for e in Overpass().query_pois():
            if 'center' in e:
                e |= e['center']

            self.pois.append(OsmPoi(
                type=e['type'],
                id=e['id'],
                tags=e['tags'],
                lat=e['lat'],
                lng=e['lon']
            ))

        self.pois = tuple(self.pois)
        self.tree = BallTree(tuple(radians_tuple((p.lat, p.lng)) for p in self.pois), metric='haversine')

    def search(self, um_pois: Sequence[UmPoi], pass_: int) -> Sequence[OsmPoi | None]:
        assert 1 <= pass_ <= 2
        search_score_threshold = OSM_SEARCH_SCORE_THRESHOLD_1 if pass_ == 1 else OSM_SEARCH_SCORE_THRESHOLD_2

        indices, distances = self.tree.query_radius(
            tuple(radians_tuple((p.lat, p.lng)) for p in um_pois),
            r=OSM_SEARCH_RADIUS_0 / EARTH_RADIUS,
            return_distance=True,
            sort_results=True)

        result = [None] * len(um_pois)

        for i, (i_distances, i_indices) in enumerate(zip(distances, indices)):
            # skip if no results
            if len(i_indices) == 0:
                continue

            um_poi = um_pois[i]
            um_poi_name = _normalize_name(um_poi.name)
            um_poi_noname = not um_poi_name
            um_poi_osm_tags = um_poi.get_osm_category_tags()

            osm_pois = tuple(self.pois[index] for index in i_indices)
            osm_pois_names = tuple(_normalize_name(p.tags.get('name', '')) for p in osm_pois)
            name_scores = process.extract(um_poi_name, osm_pois_names, scorer=fuzz.partial_token_sort_ratio)

            name_scores_map = defaultdict(float, ((i, score / 100) for _, score, i in name_scores))

            matches = [None] * len(i_indices)

            for j, (distance, osm_poi, osm_poi_name) in enumerate(zip(i_distances, osm_pois, osm_pois_names)):
                distance_meters = distance * EARTH_RADIUS
                osm_poi_noname = not osm_poi_name

                if um_poi_noname or osm_poi_noname:
                    distance_score = 1 if distance_meters < OSM_SEARCH_RADIUS_NONAME else 0
                    tags_score = _tags_score(osm_poi.tags, um_poi_osm_tags)
                    name_score = 1
                else:
                    distance_score = _distance_score(distance_meters)
                    tags_score = 1
                    name_score = name_scores_map[j]

                score = distance_score * tags_score * name_score
                assert 0 <= score <= 1, f'{score} = {distance_score} * {tags_score} * {name_score}'

                matches[j] = (-score, distance, osm_poi)

            matches.sort()
            best_match = matches[0]
            best_match_score = -best_match[0]
            best_match_osm_poi = best_match[2]

            if best_match_score >= search_score_threshold:
                result[i] = best_match_osm_poi
            else:
                print(f'✗ [{best_match_score:.3f}] {um_poi_name!r} ({um_poi.category!r}) ↔ {best_match_osm_poi.tags.get("name")!r}')

        return tuple(result)
