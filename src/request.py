from typing import NamedTuple


class Request(NamedTuple):
    producer_id: int
    id: int
    creation_time: float
