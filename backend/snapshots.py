from dataclasses import dataclass
from typing import Optional

from common.actions import QueueActions, HeapActions
from common.types import RecordedState, RecordedWindow, RecordedTeam, RecordedSnapshot, RecordedPlayer, RecordedOrder


@dataclass(kw_only=True, frozen=True)
class BaseSnapshot:
    state: Optional[RecordedState]
    order: Optional[RecordedOrder]
    add: Optional[RecordedPlayer]
    target_index: Optional[int]

    def to_dict(self) -> RecordedSnapshot:
        raise NotImplementedError("to_dict method must be implemented by subclasses of BaseSnapshot.")


@dataclass(kw_only=True, frozen=True)
class QueueSnapshot(BaseSnapshot):
    """
    Snapshot of the matchmaking queue state, including current action details and game creation attributes.
    :param state: The current state of the matchmaking queue as a list of dictionaries representing players.
    :param order: The current order of players in the queue as a list of player IDs.
    :param add: The player added to the queue during this step, represented as a dictionary
    :param window: The skill window used for matchmaking as a range of indices.
    :param target_index: The target player index involved in the queue action (p_i).
    :param team_x: The players in team X for the candidate game (X_i).
    :param team_y: The players in team Y for the candidate game (Y_i).
    :param action: The action taken on the queue.
    """
    window: Optional[RecordedWindow]
    team_x: Optional[RecordedTeam]
    team_y: Optional[RecordedTeam]
    action: QueueActions

    def to_dict(self) -> RecordedSnapshot:
        return {
            "order": self.order,
            "add": self.add,
            "window": self.window,
            "target_index": self.target_index,
            "team_x": self.team_x,
            "team_y": self.team_y,
            "action": self.action.name
        }


@dataclass(kw_only=True, frozen=True)
class HeapSnapshot(BaseSnapshot):
    """
    Snapshot of the candidate game heap state, including target game and heap action.
    :param state: The current state of the candidate game heap as a list of dictionaries representing candidate games.
    :param order: The current order of candidate games in the heap as a list of game indices.
    :param add: The candidate game added to the heap during this step, represented as a dictionary of the anchor player and the match quality metric.
    :param target_index: The target game index involved in the heap action.
    :param action: The action taken on the heap.
    """
    action: HeapActions

    def to_dict(self) -> RecordedSnapshot:
        return {
            "order": self.order,
            "add": self.add,
            "target_index": self.target_index,
            "action": self.action.name
        }
