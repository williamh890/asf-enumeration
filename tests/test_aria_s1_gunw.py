from asf_enumeration import aria_s1_gunw


def test_all_get_frames():
    frames = aria_s1_gunw.get_frames()

    assert len(frames) == 27563


def test_get_frames_by_path():
    frames = aria_s1_gunw.get_frames(path=100)

    assert all([frame.path == 100 for frame in frames])


def test_get_frames_by_flight_direction():
    ascending = aria_s1_gunw.get_frames(flight_direction='ASCENDING')
    assert all([frame.flight_direction == 'ASCENDING' for frame in ascending])

    descending = aria_s1_gunw.get_frames(flight_direction='DESCENDING')
    assert all([frame.flight_direction == 'DESCENDING' for frame in descending])
