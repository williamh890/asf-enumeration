from datetime import date
import json

import pytest

from asf_enumeration import aria_s1_gunw


def test_all_get_frames():
    frames = aria_s1_gunw.get_frames()

    assert len(frames) == 27398


def test_aria_frame_wkt():
    wkt = aria_s1_gunw.get_frame(100).wkt

    assert 'POLYGON' in wkt


def test_get_frames_by_path():
    frames = aria_s1_gunw.get_frames(path=100)

    assert all([frame.path == 100 for frame in frames])


def test_get_frames_by_flight_direction():
    ascending = aria_s1_gunw.get_frames(flight_direction='ASCENDING')
    assert all([frame.flight_direction == 'ASCENDING' for frame in ascending])

    descending = aria_s1_gunw.get_frames(flight_direction='DESCENDING')
    assert all([frame.flight_direction == 'DESCENDING' for frame in descending])


@pytest.mark.network
def test_get_stack():
    stack = aria_s1_gunw.get_stack(200)
    assert len(stack) > 0


@pytest.mark.network
def test_get_slcs():
    slcs = aria_s1_gunw.get_slcs(200, date(2025, 5, 28))

    assert slcs
