import datetime
import importlib.resources
import json
from dataclasses import dataclass


@dataclass
class AriaFrame:
    frame_id: int
    path: int
    flight_direction: str
    polygon: str

    def does_intersect(self, polygon) -> bool:
        # TODO: check intersection
        return True


def get_frames(polygon: str = None, flight_direction: str = None, path: int = None) -> list[AriaFrame]:
    flight_directions = ['ascending', 'descending'] if flight_direction is None else [flight_direction]
    aria_frames = []

    for direction in flight_directions:
        with importlib.resources.path('asf_enumeration.aria_frames', f'{direction.lower()}.geojson') as frame_file:
            frames = json.loads(frame_file.read_text())

        for frame in frames['features']:
            props = frame['properties']

            if path and path != props['path']:
                continue

            aria_frame = AriaFrame(
                frame_id=props['id'],
                path=props['path'],
                flight_direction=props['dir'],
                polygon=frame['geometry']['type']
            )

            if polygon and not aria_frame.does_intersects(polygon):
                continue

            aria_frames.append(aria_frame)

    return aria_frames


def get_stack(frame_id: int) -> list[datetime.date]:
    pass


def get_slcs(frame_id: int, date: datetime.date) -> list[str]:
    pass


def does_product_exist(frame_id: int, reference_date: datetime.date, secondary_date: datetime.date) -> bool:
    pass
