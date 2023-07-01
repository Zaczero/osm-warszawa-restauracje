import os
import secrets
from pathlib import Path

import openai
from tinydb import TinyDB

openai.api_key = os.getenv('OPENAI_KEY')
assert openai.api_key, 'OpenAI API key not set'

OSM_USERNAME = os.getenv('OSM_USERNAME')
OSM_PASSWORD = os.getenv('OSM_PASSWORD')
assert OSM_USERNAME and OSM_PASSWORD, 'OSM credentials not set'

DRY_RUN = os.getenv('DRY_RUN', None) == '1'

if DRY_RUN:
    print('🦺 TEST MODE 🦺')
else:
    print('🔴 PRODUCTION MODE 🔴')

VERSION = '1.0'
CREATED_BY = f'osm-warszawa-restauracje {VERSION}'
WEBSITE = 'https://github.com/Zaczero/osm-warszawa-restauracje'
USER_AGENT = f'osm-warszawa-restauracje/{VERSION} (+{WEBSITE})'

CACHE_DIR = Path('cache')
CACHE_DIR.mkdir(exist_ok=True)

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
DB = TinyDB(DATA_DIR / 'db.json')

# Dedicated instance unavailable? Pick one from the public list:
# https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances
OVERPASS_API_INTERPRETER = os.getenv('OVERPASS_API_INTERPRETER', 'https://overpass.monicz.dev/api/interpreter')

EARTH_RADIUS = 6371000

# TAG_MAX_LENGTH = 255

LIMIT_CHANGES_PER_CHANGESET = 20

UM_CATEGORY_TAGS = {
    '': {'amenity': 'restaurant'},
    'bar': {'amenity': 'bar'},
    'bar kawowy': {'amenity': 'cafe'},
    'bar gastronomiczny': {'amenity': 'restaurant'},
    'bar restauracyjny': {'amenity': 'restaurant'},
    'bar uniwersalny': {'amenity': 'bar'},
    'kawiarnia': {'amenity': 'cafe'},
    'klub': {'amenity': 'bar'},
    'piwiarnia': {'amenity': 'bar', 'beer': 'yes'},
    'pizzeria': {'amenity': 'restaurant', 'cuisine': 'pizza'},
    'pub': {'amenity': 'pub'},
    'restauracja': {'amenity': 'restaurant'},
    'sezonowy ogródek': {'amenity': 'restaurant'},
    'winiarnia': {'amenity': 'bar', 'wine': 'yes'},
    'zakład gastronomiczny': {'amenity': 'restaurant'},
}

UM_VALID_CATEGORIES = tuple(k for k in UM_CATEGORY_TAGS if k)

UM_GUESS_CATEGORY = {
    'bistro': 'restauracja',
    'caffe': 'kawiarnia',
    'curry': 'restauracja',
    'gastro': 'restauracja',
    'indyjska': 'restauracja',
    'kebab': 'restauracja',
    'pho': 'restauracja',
    'piwo': 'piwiarnia',
    'pizza': 'pizzeria',
    'sushi': 'restauracja',
    'tawerna': 'restauracja',
    'winiarnia': 'winiarnia',
    'zajazd': 'restauracja',
}

DEFAULT_POI_TAGS = {
    'source': 'mapa.um.warszawa.pl',
}

DEFAULT_CHANGESET_TAGS = {
    'comment': 'Import restauracji z mapy.um.warszawa.pl',
    'created_by': CREATED_BY,
    'import': 'yes',
    'source': 'mapa.um.warszawa.pl',
    'website': WEBSITE,
}

OSM_SEARCH_RADIUS_1 = 120  # meters
OSM_SEARCH_RADIUS_0 = 200  # meters
OSM_SEARCH_RADIUS_NONAME = 40  # meters

OSM_SEARCH_SCORE_THRESHOLD_1 = 0.666  # submit your soul to the devil
OSM_SEARCH_SCORE_THRESHOLD_2 = 0.750

UNICODE_QUOTES = {
    '\u2018': "'",  # LEFT SINGLE QUOTATION MARK
    '\u2019': "'",  # RIGHT SINGLE QUOTATION MARK
    '\u201A': "'",  # SINGLE LOW-9 QUOTATION MARK
    '\u201B': "'",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    '\u201C': '"',  # LEFT DOUBLE QUOTATION MARK
    '\u201D': '"',  # RIGHT DOUBLE QUOTATION MARK
    '\u201E': '"',  # DOUBLE LOW-9 QUOTATION MARK
    '\u201F': '"',  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    '\u2039': "'",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    '\u203A': "'",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    '\u300C': '"',  # LEFT CORNER BRACKET
    '\u300D': '"',  # RIGHT CORNER BRACKET
    '\u300E': '"',  # LEFT WHITE CORNER BRACKET
    '\u300F': '"',  # RIGHT WHITE CORNER BRACKET
    '\u301D': '"',  # REVERSED DOUBLE PRIME QUOTATION MARK
    '\u301E': '"',  # DOUBLE PRIME QUOTATION MARK
    '\u301F': '"',  # LOW DOUBLE PRIME QUOTATION MARK
    '\uFF02': '"',  # FULLWIDTH QUOTATION MARK
    '\uFF07': "'",  # FULLWIDTH APOSTROPHE
}

CHANGESET_ID_PLACEHOLDER = f'__CHANGESET_ID_PLACEHOLDER__{secrets.token_urlsafe(8)}__'
