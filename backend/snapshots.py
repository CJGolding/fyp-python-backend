from dataclasses import dataclass
from typing import Optional

from common.actions import QueueActions, HeapActions
from common.types import RecordedState, RecordedWindow, RecordedPlayer, RecordedTeam, RecordedGame, RecordedSnapshot


@dataclass(kw_only=True, frozen=True)
class BaseSnapshot:
    """
    Base snapshot class containing a state attribute.
    :param state: The recorded state of the component as a list of dictionaries.
    """
    state: RecordedState

    def to_dict(self) -> RecordedSnapshot:
        """Convert the BaseSnapshot instance to a dictionary for object immutability."""
        return {
            "state": self.state
        }


@dataclass(kw_only=True, frozen=True)
class QueueSnapshot(BaseSnapshot):
    """
    Snapshot of the matchmaking queue state, including current action details and game creation attributes.
    :param window: The skill window used for matchmaking as a range of indices.
    :param target_player: The target player involved in the queue action (p_i).
    :param team_x: The players in team X for the candidate game (X_i).
    :param team_y: The players in team Y for the candidate game (Y_i).
    :param action: The action taken on the queue.
    """
    window: Optional[RecordedWindow]
    target_player: Optional[RecordedPlayer]
    team_x: Optional[RecordedTeam]
    team_y: Optional[RecordedTeam]
    action: QueueActions

    def to_dict(self) -> RecordedSnapshot:
        result = super().to_dict()
        result.update({
            "skill_window": self.window,
            "target_player": self.target_player,
            "team_x": self.team_x,
            "team_y": self.team_y,
            "action": self.action.name if self.action else None
        })
        return result


@dataclass(kw_only=True, frozen=True)
class HeapSnapshot(BaseSnapshot):
    """
    Snapshot of the candidate game heap state, including target game and heap action.
    :param target_game: The target game involved in the heap action.
    :param action: The action taken on the heap.
    """
    target_game: Optional[RecordedGame]
    action: HeapActions

    def to_dict(self) -> RecordedSnapshot:
        result = super().to_dict()
        result.update({
            "target_game": self.target_game,
            "action": self.action.name if self.action else None
        })
        return result
