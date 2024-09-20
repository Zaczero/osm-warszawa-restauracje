import os
import secrets
from pathlib import Path

from openai import OpenAI
from tinydb import TinyDB

OPENAI = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
OSM_TOKEN = os.environ['OSM_TOKEN']
DRY_RUN = os.getenv('DRY_RUN', None) == '1'

if DRY_RUN:
    print('🦺 TEST MODE 🦺')
else:
    print('🔴 PRODUCTION MODE 🔴')

VERSION = '1.5.1'
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
    'azjatycka': {'amenity': 'restaurant', 'cuisine': 'asian'},
    'bar': {'amenity': 'bar'},
    'bar kawowy': {'amenity': 'cafe'},
    'bar gastronomiczny': {'amenity': 'restaurant'},
    'bar restauracyjny': {'amenity': 'restaurant'},
    'bar uniwersalny': {'amenity': 'bar'},
    'burgerownia': {'amenity': 'restaurant', 'cuisine': 'burger'},
    'chińska': {'amenity': 'restaurant', 'cuisine': 'chinese'},
    'cukiernia': {'shop': 'confectionery'},
    'grecka': {'amenity': 'restaurant', 'cuisine': 'greek'},
    'grill': {'amenity': 'restaurant', 'cuisine': 'grill'},
    'indyjska': {'amenity': 'restaurant', 'cuisine': 'indian'},
    'japońska': {'amenity': 'restaurant', 'cuisine': 'japanese'},
    'kawiarnia': {'amenity': 'cafe'},
    'kebab': {'amenity': 'restaurant', 'cuisine': 'kebab'},
    'klub': {'amenity': 'bar'},
    'koreańska': {'amenity': 'restaurant', 'cuisine': 'korean'},
    'lodziarnia': {'amenity': 'ice_cream'},
    'piekarnia': {'shop': 'bakery'},
    'pierogarnia': {'amenity': 'restaurant', 'cuisine': 'dumplings'},
    'piwiarnia': {'shop': 'alcohol'},
    'pizzeria': {'amenity': 'restaurant', 'cuisine': 'pizza'},
    'pub': {'amenity': 'pub'},
    'ramen': {'amenity': 'restaurant', 'cuisine': 'ramen'},
    'restauracja': {'amenity': 'restaurant'},
    'sushi': {'amenity': 'restaurant', 'cuisine': 'sushi'},
    'sezonowy ogródek': {'amenity': 'restaurant'},
    'thai': {'amenity': 'restaurant', 'cuisine': 'thai'},
    'winiarnia': {'shop': 'wine'},
    'zakład gastronomiczny': {'amenity': 'restaurant'},
}

UM_VALID_CATEGORIES = tuple(k for k in UM_CATEGORY_TAGS if k)

UM_GUESS_CATEGORY = {
    'bistro': 'restauracja',
    'burger': 'burgerownia',
    'cafe': 'kawiarnia',
    'caffe': 'kawiarnia',
    'coffe': 'kawiarnia',
    'coffee': 'kawiarnia',
    'ciastkarnia': 'cukiernia',
    'club': 'klub',
    'curry': 'restauracja',
    'gastro': 'restauracja',
    'karczma': 'restauracja',
    'kawa': 'kawiarnia',
    'kawy': 'kawiarnia',
    'lody': 'lodziarnia',
    'naleśnikarnia': 'cukiernia',
    'pho': 'restauracja',
    'pierogi': 'pierogarnia',
    'piwa': 'piwiarnia',
    'piwo': 'piwiarnia',
    'piwny': 'piwiarnia',
    'pizza': 'pizzeria',
    'restaurant': 'restauracja',
    'ristorante': 'restauracja',
    'tawerna': 'restauracja',
    'zajazd': 'restauracja',
}

if set(UM_CATEGORY_TAGS).intersection(UM_GUESS_CATEGORY):
    raise RuntimeError('UM_CATEGORY_TAGS and UM_GUESS_CATEGORY must be disjoint')

DEFAULT_POI_TAGS = {
    'source': 'mapa.um.warszawa.pl',
}

DEFAULT_CHANGESET_TAGS = {
    'comment': 'Import restauracji z mapy.um.warszawa.pl',
    'created_by': CREATED_BY,
    'import': 'yes',
    'source': 'mapa.um.warszawa.pl',
    'website': WEBSITE,
    'website:import': 'https://wiki.openstreetmap.org/wiki/Restaurants_import_in_Warsaw',
}

OSM_SEARCH_RADIUS_1 = 200  # meters
OSM_SEARCH_RADIUS_0 = 300  # meters
OSM_SEARCH_RADIUS_NONAME = 50  # meters

OSM_SEARCH_SCORE_THRESHOLD_1 = 0.666  # submit your soul to the devil
OSM_SEARCH_SCORE_THRESHOLD_2 = 0.750

UNICODE_QUOTES = {
    '\u2018': "'",  # LEFT SINGLE QUOTATION MARK
    '\u2019': "'",  # RIGHT SINGLE QUOTATION MARK
    '\u201a': "'",  # SINGLE LOW-9 QUOTATION MARK
    '\u201b': "'",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    '\u201c': '"',  # LEFT DOUBLE QUOTATION MARK
    '\u201d': '"',  # RIGHT DOUBLE QUOTATION MARK
    '\u201e': '"',  # DOUBLE LOW-9 QUOTATION MARK
    '\u201f': '"',  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    '\u2039': "'",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    '\u203a': "'",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    '\u300c': '"',  # LEFT CORNER BRACKET
    '\u300d': '"',  # RIGHT CORNER BRACKET
    '\u300e': '"',  # LEFT WHITE CORNER BRACKET
    '\u300f': '"',  # RIGHT WHITE CORNER BRACKET
    '\u301d': '"',  # REVERSED DOUBLE PRIME QUOTATION MARK
    '\u301e': '"',  # DOUBLE PRIME QUOTATION MARK
    '\u301f': '"',  # LOW DOUBLE PRIME QUOTATION MARK
    '\uff02': '"',  # FULLWIDTH QUOTATION MARK
    '\uff07': "'",  # FULLWIDTH APOSTROPHE
}

CHANGESET_ID_PLACEHOLDER = f'__CHANGESET_ID_PLACEHOLDER__{secrets.token_urlsafe(8)}__'
