from added_db import filter_added, mark_added
from ai_name_convert import ai_name_convert
from config import DRY_RUN, LIMIT_CHANGES_PER_CHANGESET
from openstreetmap import OpenStreetMap
from osm_change import create_pois
from osm_search import OsmSearch
from um_fetch import um_fetch_restaurants
from um_poi import UmPoi
from utils import beautify_name, print_run_time


def main():
    with print_run_time('Logging in'):
        osm = OpenStreetMap()
        display_name = osm.get_authorized_user()['display_name']
        print(f'👤 Welcome, {display_name}!')

    with print_run_time('Fetching UM restaurants'):
        um_pois = um_fetch_restaurants()

    with print_run_time('Filtering added POIs'):
        um_pois = filter_added(um_pois)

    with print_run_time('Initializing OSM search'):
        osm_search = OsmSearch()

    with print_run_time('Searching OSM'):
        osm_matches = osm_search.search(um_pois, pass_=1)

    missing_pois: list[UmPoi] = []

    for um_poi, osm_match in zip(um_pois, osm_matches, strict=True):
        um_poi_name = beautify_name(um_poi.name)

        if not um_poi_name:
            continue

        if osm_match is None:
            missing_pois.append(um_poi)
            print(f'[1/2] ❌ {um_poi_name!r} ({um_poi.category!r})')
        else:
            osm_match_name = beautify_name(osm_match.tags.get('name'))
            print(f'[1/2] ✅ {um_poi_name!r} ({um_poi.category!r}) ↔ {osm_match_name!r}')
            mark_added((um_poi,), reason='exists_1')

    um_pois = ai_name_convert(missing_pois)
    missing_pois.clear()

    with print_run_time('Searching OSM (2nd pass)'):
        osm_matches = osm_search.search(um_pois, pass_=2)

    for um_poi, osm_match in zip(um_pois, osm_matches, strict=True):
        um_poi_name = beautify_name(um_poi.name)

        if not um_poi_name:
            continue

        if osm_match is None:
            missing_pois.append(um_poi)
            print(f'[2/2] ❌ {um_poi_name!r} ({um_poi.category!r})')
        else:
            osm_match_name = beautify_name(osm_match.tags.get('name'))
            print(f'[2/2] ✅ {um_poi_name!r} ({um_poi.category!r}) ↔ {osm_match_name!r}')
            mark_added((um_poi,), reason='exists_2')

    missing_pois = missing_pois[:LIMIT_CHANGES_PER_CHANGESET]
    print(f'🛟 Limiting to {LIMIT_CHANGES_PER_CHANGESET} POIs')
    print(f'📍 Total POIs to be added: {len(missing_pois)}')

    if not missing_pois:
        print('0️⃣ Nothing to do')
        return

    with print_run_time('Creating OSM changeset'):
        osm_change = create_pois(missing_pois)

    if not DRY_RUN:
        with print_run_time('Uploading OSM changeset'):
            osm.upload_osm_change(osm_change)

        mark_added(missing_pois)

    print('✅ Import complete')


if __name__ == '__main__':
    main()
