from enum import Enum


class PublishErrorType(str, Enum):
    AUTH = "auth"
    RATE_LIMIT = "rate_limit"
    SERVER = "server"
    CLIENT = "client"
    UNKNOWN = "unknown"
