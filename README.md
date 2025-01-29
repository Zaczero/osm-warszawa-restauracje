# osm-warszawa-restauracje

![Python version](https://shields.monicz.dev/badge/python-v3.13-blue)
[![Liberapay Patrons](https://shields.monicz.dev/liberapay/patrons/Zaczero?logo=liberapay)](https://liberapay.com/Zaczero/)
[![GitHub Sponsors](https://shields.monicz.dev/github/sponsors/Zaczero?logo=github&label=Sponsors&color=%23db61a2)](https://github.com/sponsors/Zaczero)

🏙️ OpenStreetMap import tool for restaurants from [mapa.um.warszawa.pl](https://mapa.um.warszawa.pl)

## 💡 How it works

1. Fetches data from [mapa.um.warszawa.pl](https://mapa.um.warszawa.pl) and adds missing POI categories based on names.
2. Filters out already once imported restaurants to avoid re-importing deleted ones.
3. Fetches and parses OpenStreetMap data for Warsaw.
4. Filters out already existing restaurants by comparing names and locations.
5. Transforms names to match OpenStreetMap naming convention using [OpenAI GPT-4o](https://openai.com/index/hello-gpt-4o/).
6. Repeats step 4 with modified parameters.
7. Uploads new restaurants to OpenStreetMap.

## Reference

### Community discussion

<https://community.openstreetmap.org/t/warszawa-import-restauracji-z-mapa-um-warszawa-pl/97607/>

### Data usage terms

<https://mapa.um.warszawa.pl/warunki.html>
