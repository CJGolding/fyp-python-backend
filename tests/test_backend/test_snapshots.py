from common.actions import HeapActions, QueueActions
from backend import BaseSnapshot, HeapSnapshot, QueueSnapshot

def test_base_snapshot_to_dict() -> None:
    snapshot = BaseSnapshot(state=[{"id": 1, "skill": 100}])
    snapshot_dict = snapshot.to_dict()
    assert snapshot_dict == {"state": [{"id": 1, "skill": 100}]}

def test_queue_snapshot_to_dict() -> None:
    snapshot = QueueSnapshot(
        state=[{"id": 1, "skill": 100}],
        window={0, 1},
        target_player=1,
        team_x={1},
        team_y={2},
        action=QueueActions.IDLE
    )
    snapshot_dict = snapshot.to_dict()
    assert snapshot_dict == {
        "state": [{"id": 1, "skill": 100}],
        "skill_window": {0, 1},
        "target_player": 1,
        "team_x": {1},
        "team_y": {2},
        "action": "IDLE"
    }

def test_heap_snapshot_to_dict() -> None:
    snapshot = HeapSnapshot(
        state=[{"anchor_player_id": 1, "team_x": [1], "team_y": [2], "imbalance": 0.0}],
        target_game=None,
        action=HeapActions.IDLE
    )
    snapshot_dict = snapshot.to_dict()
    assert snapshot_dict == {
        "state": [{"anchor_player_id": 1, "team_x": [1], "team_y": [2], "imbalance": 0.0}],
        "target_game": None,
        "action": "IDLE"
    }