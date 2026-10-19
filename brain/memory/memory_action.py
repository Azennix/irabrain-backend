from enum import Enum


class MemoryAction(Enum):
    """
    Represents what action the Memory Engine should perform.
    """

    STORE = "store"
    RETRIEVE = "retrieve"
    NONE = "none"