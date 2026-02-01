from enum import Enum

class Status(str, Enum):
    TRACK = "TRACK"
    WHITELIST = "WHITELIST"
    CANDIDATE = "CANDIDATE"
    CHURNED = "CHURNED"
