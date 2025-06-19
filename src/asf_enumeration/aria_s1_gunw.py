import datetime
from dataclasses import dataclass


@dataclass
class AriaFrame:
    frame_id: int
    path: int
    flight_direction: str


def get_frames(polygon: str = None, flight_direction: str = None, path: int = None) -> list[AriaFrame]:
    pass


def get_stack(frame_id: int) -> list[datetime.date]:
    pass


def get_slcs(frame_id: int, date: datetime.date) -> list[str]:
    pass


def does_product_exist(frame_id: int, reference_date: datetime.date, secondary_date: datetime.date) -> bool:
    pass
