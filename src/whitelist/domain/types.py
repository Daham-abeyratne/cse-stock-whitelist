from enum import Enum

class Status(str, Enum):
    TRACK = "TRACK"
    WHITELIST = "WHITELIST"
    CHURNED = "CHURNED"
