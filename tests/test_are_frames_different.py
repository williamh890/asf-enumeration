import importlib.resources
import json
from collections import defaultdict

import pytest
import shapely

import asf_enumeration


@pytest.mark.skip
def test_if_frames_are_different():
    all_frames = defaultdict(set)
    duplicates = 0

    for direction in ['ascending', 'descending']:
        with importlib.resources.path('asf_enumeration.aria_frames', f'{direction}.geojson') as frame_file:
            frames = json.loads(frame_file.read_text())

        for frame in frames['features']:
            props = frame['properties']

            aria_frame = asf_enumeration.aria.AriaFrame(
                frame_id=props['id'],
                path=props['path'],
                flight_direction=props['dir'],
                polygon=shapely.Polygon(frame['geometry']['coordinates'][0]),
            )
            if aria_frame.frame_id in all_frames:
                duplicates += 1

            all_frames[aria_frame.frame_id].add(aria_frame)

    print(f'found {duplicates} duplicate frames')
    for frame_set in all_frames.values():
        assert len(frame_set) == 1


@pytest.mark.skip
def test_consolidate_frame_map():
    all_frames = []
    frame_ids = set()

    for direction in ['ascending', 'descending']:
        with importlib.resources.path('asf_enumeration.aria_frames', f'{direction}.geojson') as frame_file:
            frames = json.loads(frame_file.read_text())

        for frame in frames['features']:
            props = frame['properties']

            if props['id'] in frame_ids:
                continue

            frame_ids.add(props['id'])
            all_frames.append(frame)

    with open('./frames.geojson', 'w') as f:
        json.dump({'type': 'FeatureCollection', 'features': all_frames}, f)

    print(len(all_frames))
