import datetime
import importlib.resources
import json
from collections import defaultdict
from dataclasses import dataclass

import requests


SEARCH_API_URL = 'https://api-prod-private.asf.alaska.edu/services/search/param'


@dataclass
class AriaFrame:
    frame_id: int
    path: int
    flight_direction: str
    geometry: dict

    def does_intersect(self, polygon) -> bool:
        # TODO: check intersection
        return True

    @property
    def wkt(self) -> str:
        coordinates = ','.join(' '.join(str(coord) for coord in point) for point in self.geometry['coordinates'][0])
        return f'POLYGON(({coordinates}))'


def _load_aria_frames_by_id() -> dict[int, AriaFrame]:
    frames_by_id = {}

    for direction in ['ascending', 'descending']:
        with importlib.resources.path('asf_enumeration.aria_frames', f'{direction}.geojson') as frame_file:
            frames = json.loads(frame_file.read_text())

        for frame in frames['features']:
            props = frame['properties']

            aria_frame = AriaFrame(
                frame_id=props['id'],
                path=props['path'],
                flight_direction=props['dir'],
                geometry=frame['geometry']
            )

            frames_by_id[aria_frame.frame_id] = aria_frame

    return frames_by_id


FRAMES_BY_ID = _load_aria_frames_by_id()


def get_frames(polygon: str = None, flight_direction: str = None, path: int = None) -> list[AriaFrame]:
    aria_frames = []

    for frame in FRAMES_BY_ID.values():
        if flight_direction and flight_direction.upper() != frame.flight_direction:
            continue

        if path and path != frame.path:
            continue

        if polygon and not frame.does_intersects(polygon):
            continue

        aria_frames.append(frame)

    return aria_frames


def get_frame(frame_id: int) -> AriaFrame:
    return FRAMES_BY_ID[frame_id]


def get_stack(frame_id: int) -> list[datetime.date]:
    granules = _get_granules_for_frame(frame_id)
    stack_dates = _get_stack_dates_from(granules)
    stack_dates.sort()
    return stack_dates


def _get_granules_for_frame(frame_id: int, date: datetime.date = None) -> list[dict]:
    frame = get_frame(frame_id)

    params = {
        'dataset': 'SENTINEL-1',
        'processingLevel': 'SLC',
        'beamMode': 'IW',
        'polarization': 'VV,VV+VH',
        'flightDirection': frame.flight_direction,
        'relativeOrbit': frame.path,
        'intersectsWith': frame.wkt,
        'output': 'jsonlite2',
    }

    if date:
        params['start'] = date.isoformat()
        params['end'] = (date + datetime.timedelta(days=1)).isoformat()

    response = requests.get(SEARCH_API_URL, params=params)
    response.raise_for_status()
    return response.json()['results']


def _get_stack_dates_from(granules: list[dict]) -> list[datetime.date]:
    groups = defaultdict(list)
    for granule in granules:
        group_id = granule['d'] + '_' + granule['o'][0]
        groups[group_id].append(granule)
    granule_dates = [min(datetime.datetime.fromisoformat(g['st']).date() for g in group) for group in groups.values()]
    return granule_dates


def get_slcs(frame_id: int, date: datetime.date) -> list[str]:
    slcs = _get_granules_for_frame(frame_id, date)

    return slcs


def does_product_exist(frame_id: int, reference_date: datetime.date, secondary_date: datetime.date) -> bool:
    params = {
        'dataset': 'ARIA S1 GUNW',
        'frame': frame_id,
        'output': 'jsonlite2',
        'start': (reference_date - datetime.timedelta(days=1)).isoformat(),
        'end': (reference_date + datetime.timedelta(days=1)).isoformat()
    }

    response = requests.get(SEARCH_API_URL, params=params)
    response.raise_for_status()
    granules = [result['gn'] for result in response.json()['results']]

    return any([_dates_match(g, reference_date, secondary_date) for g in granules])


def _dates_match(granule: str, reference: datetime.date, secondary: datetime.date) -> bool:
    granule_reference, granule_secondary = [
        datetime.datetime.strptime(date_str, '%Y%m%d').date() for date_str in granule.split('-')[6].split('_')
    ]

    return granule_reference == reference and granule_secondary == secondary
