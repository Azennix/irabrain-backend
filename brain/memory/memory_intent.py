from enum import Enum


class MemoryIntent(Enum):

    UNKNOWN = "unknown"

    STORE = "store"

    RECALL = "recall"

    UPDATE = "update"

    DELETE = "delete"