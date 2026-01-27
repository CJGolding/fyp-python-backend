from sortedcontainers import SortedSet
from backend import Recorder, MinHeap, Player, CandidateGame

def test_when_instantiating_recorder_then_initialise_attributes() -> None:
    recorder = Recorder()

    assert recorder.steps == []
    assert recorder.queue_size == []
    assert recorder.heap_size == []
    assert recorder.max_wait_time == []

def test_when_clearing_recorder_then_steps_are_cleared() -> None:
    recorder = Recorder()
    dummy_step = {
        "queue_state": SortedSet(),
        "heap_state": MinHeap(),
        "created_matches": []
    }
    recorder.record_step(**dummy_step)
    assert len(recorder.steps) == 1

    recorder._Recorder__clear()
    assert len(recorder.steps) == 0

def test_when_recording_step_then_step_is_added_and_stats_updated() -> None:
    recorder = Recorder()
    dummy_step = {
        "queue_state": SortedSet(),
        "heap_state": MinHeap(),
        "created_matches": []
    }
    recorder.record_step(**dummy_step)
    assert len(recorder.steps) == 1
    assert recorder.queue_size == [0]
    assert recorder.heap_size == [0]
    assert recorder.max_wait_time == [0]

def test_when_preserve_queue_then_previous_queue_is_copied() -> None:
    recorder = Recorder()
    dummy_step1 = {
        "queue_state": SortedSet([Player(player_id=1, skill=100)]),
        "heap_state": MinHeap(),
        "created_matches": []
    }
    recorder.record_step(**dummy_step1)

    dummy_step2 = {
        "heap_state": MinHeap(),
        "created_matches": [],
        "preserve_queue": True
    }
    recorder.record_step(**dummy_step2)

    assert recorder.steps[1].queue_snapshot.state == recorder.steps[0].queue_snapshot.state

def test_when_preserve_heap_then_previous_heap_is_copied() -> None:
    recorder = Recorder()
    heap = MinHeap()
    heap.push(CandidateGame(Player(player_id=1, skill=100), {Player(player_id=1, skill=100)}, {
        Player(player_id=2, skill=150)}, 1.0, 1.0, 0.1))
    dummy_step1 = {
        "queue_state": SortedSet(),
        "heap_state": heap,
        "created_matches": []
    }
    recorder.record_step(**dummy_step1)

    dummy_step2 = {
        "queue_state": SortedSet(),
        "created_matches": [],
        "preserve_heap": True
    }
    recorder.record_step(**dummy_step2)

    assert recorder.steps[1].heap_snapshot.state == recorder.steps[0].heap_snapshot.state