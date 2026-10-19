from enum import Enum


class MemoryCategory(Enum):
    """
    Defines the standard memory categories used by IRABRAIN.
    """

    IDENTITY = "identity"
    GOAL = "goal"
    PROJECT = "project"
    PREFERENCE = "preference"
    SKILL = "skill"
    RELATIONSHIP = "relationship"
    EDUCATION = "education"
    CAREER = "career"
    LOCATION = "location"
    FACT = "fact"
    EXPERIENCE = "experience"
    CONTEXT = "context"