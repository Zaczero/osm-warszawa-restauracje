import httpx
import xmltodict

from config import CHANGESET_ID_PLACEHOLDER, DEFAULT_CHANGESET_TAGS, OSM_TOKEN
from utils import get_http_client


class OpenStreetMap:
    def _get_http_client(self) -> httpx.Client:
        return get_http_client('https://api.openstreetmap.org/api', headers={'Authorization': f'Bearer {OSM_TOKEN}'})

    def get_authorized_user(self) -> dict | None:
        with self._get_http_client() as http:
            r = http.get('/0.6/user/details.json')
            r.raise_for_status()

        return r.json()['user']

    def upload_osm_change(self, osm_change: str) -> None:
        changeset = xmltodict.unparse(
            {
                'osm': {
                    'changeset': {
                        'tag': [
                            {
                                '@k': k,
                                '@v': v,
                            }
                            for k, v in DEFAULT_CHANGESET_TAGS.items()
                        ]
                    }
                }
            }
        )

        with self._get_http_client() as http:
            r = http.put(
                '/0.6/changeset/create',
                content=changeset,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                follow_redirects=False,
            )
            r.raise_for_status()

            changeset_id = r.text
            osm_change = osm_change.replace(CHANGESET_ID_PLACEHOLDER, changeset_id)
            print(f'🌐 Changeset: https://www.openstreetmap.org/changeset/{changeset_id}')

            upload_resp = http.post(
                f'/0.6/changeset/{changeset_id}/upload',
                content=osm_change,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                timeout=150,
            )

            r = http.put(f'/0.6/changeset/{changeset_id}/close')
            r.raise_for_status()

        if not upload_resp.is_success:
            raise Exception(f'Upload failed ({upload_resp.status_code}): {upload_resp.text}')
