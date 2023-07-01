from osm_search import OsmSearch
from um_fetch import um_fetch_restaurants
from utils import beautify_name, print_run_time


def main():
    with print_run_time('Fetching UM restaurants'):
        um_pois = um_fetch_restaurants()

    with print_run_time('Initializing OSM search'):
        osm_search = OsmSearch()

    with print_run_time('Searching OSM'):
        osm_matches = osm_search.search(um_pois)

    for um_poi, osm_match in zip(um_pois, osm_matches):
        um_poi_name = beautify_name(um_poi.name)

        if osm_match is None:
            print(f'❌ {um_poi_name!r} ({um_poi.category!r})')
        else:
            print(f'✅ {um_poi_name!r} ({um_poi.category!r}) ↔ {osm_match.tags["name"]!r}')


if __name__ == '__main__':
    main()
