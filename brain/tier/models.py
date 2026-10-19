from enum import Enum


class BrainTier(str, Enum):
    FREE = "FREE"
    STARTER = "STARTER"
    BRAIN_MINI = "BRAIN_MINI"
    BRAIN_ORION = "BRAIN_ORION"
    THALAMUS = "THALAMUS"
    HIPPOCAMPUS = "HIPPOCAMPUS"