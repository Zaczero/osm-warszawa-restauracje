import os

VERSION = '1.0'
CREATED_BY = f'osm-warszawa-restauracje {VERSION}'
USER_AGENT = f'osm-warszawa-restauracje/{VERSION} (+https://github.com/Zaczero/osm-warszawa-restauracje)'

# Dedicated instance unavailable? Pick one from the public list:
# https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances
OVERPASS_API_INTERPRETER = os.getenv('OVERPASS_API_INTERPRETER', 'https://overpass.monicz.dev/api/interpreter')

EARTH_RADIUS = 6371000

TAG_MAX_LENGTH = 255

UM_CATEGORY_TAGS = {
    '': {},
    'bar': {'amenity': 'bar'},
    'kawiarnia': {'amenity': 'cafe'},
    'pizzeria': {'amenity': 'restaurant', 'cuisine': 'pizza'},
    'restauracja': {'amenity': 'restaurant'},
}

UM_VALID_CATEGORIES = tuple(k for k in UM_CATEGORY_TAGS if k)

UM_GUESS_CATEGORY = {
    'caffe': 'kawiarnia',
    'curry': 'restauracja',
    'gastro': 'restauracja',
    'indyjska': 'restauracja',
    'kebab': 'restauracja',
    'klub': 'bar',
    'pho': 'restauracja',
    'pizza': 'pizzeria',
    'sushi': 'restauracja',
}

DEFAULT_POI_TAGS = {
    'source': 'mapa.um.warszawa.pl',
}

DEFAULT_CHANGESET_TAGS = {
}

OSM_SEARCH_RADIUS_1 = 120  # meters
OSM_SEARCH_RADIUS_0 = 200  # meters
OSM_SEARCH_RADIUS_NONAME = 40  # meters

OSM_SEARCH_SCORE_THRESHOLD = 0.7

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
