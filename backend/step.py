from typing import Optional

from backend.snapshots import QueueSnapshot, HeapSnapshot
from common.actions import QueueActions, HeapActions
from common.types import (RecordedStep, RecordedWindow, Player, RecordedTeam, RecordedGame, MinHeap, SortedSet,
                          CandidateGame, RecordedPlayerIndex)


class Step:
    def __init__(self, queue_state: SortedSet = None, heap_state: MinHeap = None,
                 window: Optional[RecordedWindow] = None, target_player: Optional[RecordedPlayerIndex] = None,
                 team_x: Optional[RecordedTeam] = None, team_y: Optional[RecordedTeam] = None,
                 add_player: Player = None, add_game: Optional[CandidateGame] = None,
                 queue_action: QueueActions = QueueActions.IDLE, target_game: Optional[RecordedGame] = None,
                 heap_action: HeapActions = HeapActions.IDLE) -> None:
        """
        Represents a single step in the matchmaking process, capturing snapshots of the queue, heap, and created matches.
        :param queue_state: Current state of the matchmaking queue as a SortedSet of Players.
        :param heap_state: Current state of the candidate game heap as a MinHeap of CandidateGames.
        :param window: Optional skill window used in the queue snapshot as a range of indices.
        :param target_player: Optional target player index involved in the queue action.
        :param team_x: Optional list of player indices in team X for the queue snapshot.
        :param team_y: Optional list of player indices in team Y for the queue snapshot.
        :param add_player: Optional player added to the queue during this step.
        :param add_game: Optional candidate game added to the heap during this step.
        :param queue_action: Action taken on the queue during this step.
        :param target_game: Optional target game index involved in the heap action.
        :param heap_action: Action taken on the heap during this step.
        """
        self.queue_snapshot: QueueSnapshot = QueueSnapshot(
            state=[player.to_dict() for player in queue_state],
            order=[player.id for player in queue_state],
            add=add_player.to_dict() if add_player else None,
            window=window,
            target_index=target_player,
            team_x=list(team_x or []),
            team_y=list(team_y or []),
            action=queue_action
        )
        self.heap_snapshot: HeapSnapshot = HeapSnapshot(
            state=[game.to_dict() for game in heap_state],
            order=[game.anchor_player.id for game in heap_state],
            add=add_game.to_dict() if add_game else None,
            target_index=target_game,
            action=heap_action
        )

    def to_dict(self) -> RecordedStep:
        """Convert the Step instance to a dictionary for object immutability."""
        return {
            "queue_snapshot": self.queue_snapshot.to_dict(),
            "heap_snapshot": self.heap_snapshot.to_dict(),
        }
