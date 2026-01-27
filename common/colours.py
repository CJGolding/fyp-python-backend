from enum import StrEnum


class Colours(StrEnum):
    """
    Defines a set of standard colours for use in the application.
    Uses StrEnum for easy string representation of colour codes.
    """
    DEFAULT = "#e0e0e0"
    WINDOW = "#bbdefb"
    TEAM_X = "#4caf50"
    TEAM_Y = "#ff9800"
    ANCHOR = "#ce93d8"
    INSERTED = "#c8e6c9"
    REMOVED = "#ffcdd2"
    NODE = "#e3f2fd"
    ROOT = "#e1bee7"
    NEW_NODE = "#fff3e0"
    REMOVED_NODE = "#ffcdd2"
    TEXT_DARK = "#333333"
    TEXT_LIGHT = "#ffffff"
    MATCH_NODE = "#aed581"
