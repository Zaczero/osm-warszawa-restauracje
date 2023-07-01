# osm-warszawa-restauracje

![Python version](https://shields.monicz.dev/github/pipenv/locked/python-version/Zaczero/osm-warszawa-restauracje)
[![Project license](https://shields.monicz.dev/github/license/Zaczero/osm-warszawa-restauracje)](https://github.com/Zaczero/osm-warszawa-restauracje/blob/main/LICENSE)
[![Support my work](https://shields.monicz.dev/badge/%E2%99%A5%EF%B8%8F%20Support%20my%20work-purple)](https://monicz.dev/#support-my-work)
[![GitHub repo stars](https://shields.monicz.dev/github/stars/Zaczero/osm-warszawa-restauracje?style=social)](https://github.com/Zaczero/osm-warszawa-restauracje)

🏙️ OpenStreetMap import tool for restaurants from [mapa.um.warszawa.pl](https://mapa.um.warszawa.pl)

## 💡 How it works

1. Fetches data from [mapa.um.warszawa.pl](https://mapa.um.warszawa.pl) and adds missing POI categories based on names.
2. Filters out already once imported restaurants to avoid re-importing deleted ones.
3. Fetches and parses OpenStreetMap data for Warsaw.
4. Filters out already existing restaurants by comparing names and locations.
5. Transforms names to match OpenStreetMap naming convention using [OpenAI GPT-3](https://en.wikipedia.org/wiki/GPT-3).
6. Repeats step 4 with modified parameters.
7. Uploads new restaurants to OpenStreetMap.

## Reference

### Data usage terms

https://mapa.um.warszawa.pl/warunki.html

## Footer

### Contact me

https://monicz.dev/#get-in-touch

### Support my work

https://monicz.dev/#support-my-work

### License

This project is licensed under the GNU Affero General Public License v3.0.

The complete license text can be accessed in the repository at [LICENSE](https://github.com/Zaczero/osm-warszawa-restauracje/blob/main/LICENSE).
