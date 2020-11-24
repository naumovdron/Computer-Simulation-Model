from src.request import *


class CreationEvent(NamedTuple):
    time: float
    producer_id: int
    id: int


class ReleaseEvent(NamedTuple):
    time: float
    device_index: int
    request: Request


class SettingEvent(NamedTuple):
    time: float
    device_index: int
    request: Request


class DenyEvent(NamedTuple):
    time: float
    request: Request
