import pytest
from sortedcontainers import SortedSet

from backend import Step, Player, CandidateGame, MinHeap
from common.actions import QueueActions, HeapActions


def test_step_to_dict() -> None:
    min_heap = MinHeap()
    min_heap.push(CandidateGame(Player(id=1, skill=100), {Player(id=1, skill=100)}, {Player(id=2, skill=150)}, 1.0, 1.0, 0.1))
    step = Step(
        created_matches=[],
        queue_state=SortedSet([Player(id=1, skill=100), Player(id=2, skill=150)]),
        heap_state=min_heap
    )
    step_dict = step.to_dict()
    assert sorted(list(step_dict.keys())) == sorted(["queue_snapshot", "heap_snapshot", "created_matches"])
    for player in step_dict["queue_snapshot"]["state"]:
        assert sorted(list(player.keys())) == sorted(["id", "skill", "enqueue_time", "wait_time"])
    for game in step_dict["heap_snapshot"]["state"]:
        assert sorted(list(game.keys())) == sorted(["anchor_player_id", "team_x", "team_y", "imbalance"])
    assert step_dict["created_matches"]["state"] == []

def test_when_providing_snapshots_then_they_are_used() -> None:
    from backend.snapshots import QueueSnapshot, HeapSnapshot

    custom_queue_snapshot = QueueSnapshot(
        state=[{"id": 1, "skill": 100, "enqueue_time": 0, "wait_time": 0}],
        window={0, 1},
        target_player=1,
        team_x={1},
        team_y={2},
        action=QueueActions.IDLE
    )
    custom_heap_snapshot = HeapSnapshot(
        state=[{"anchor_player_id": 1, "team_x": [1], "team_y": [2], "imbalance": 0.0}],
        target_game=None,
        action=HeapActions.IDLE
    )
    step = Step(
        created_matches=[],
        queue_snapshot=custom_queue_snapshot,
        heap_snapshot=custom_heap_snapshot
    )
    assert step.queue_snapshot == custom_queue_snapshot
    assert step.heap_snapshot == custom_heap_snapshot

def test_when_missing_state_and_snapshots_then_error_is_raised() -> None:
    with pytest.raises(TypeError) as e:
        Step(created_matches=[])

    assert str(e.value) == "'NoneType' object is not iterable"