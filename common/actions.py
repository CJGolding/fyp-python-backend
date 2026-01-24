from enum import Enum


class HeapActions(Enum):
    """Defined actions that can be performed on the game heap."""
    INSERT = 1
    REMOVE = 2
    IDLE = 3


class QueueActions(Enum):
    """Defined actions that can be performed on the player queue."""
    ANCHOR = 1
    INSERT = 2
    REMOVE = 3
    GAME_FOUND = 4
    GAME_NOT_FOUND = 5
    IDLE = 6
