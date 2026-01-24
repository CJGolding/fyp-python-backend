from backend import Player

def test_player_to_dict() -> None:
    player = Player(id=1, skill=100)
    player_dict = player.to_dict()
    assert sorted(list(player_dict.keys())) == sorted(["id", "skill", "enqueue_time", "wait_time"])

def test_when_marking_player_as_exited_then_dequeue_time_is_set() -> None:
    player = Player(id=1, skill=100)
    assert player.dequeue_time is None
    player.mark_as_exited()
    assert player.dequeue_time is not None
    assert player.dequeue_time >= player.enqueue_time
    assert player.wait_time == player.dequeue_time - player.enqueue_time

def test_when_players_have_same_skill_then_comparison_uses_id() -> None:
    player1 = Player(id=1, skill=100)
    player2 = Player(id=2, skill=100)
    assert player1 < player2
    assert not (player2 < player1)

def test_when_player_ids_are_equal_then_players_are_equal() -> None:
    player1 = Player(id=1, skill=100)
    player2 = Player(id=1, skill=200)
    assert player1 == player2
    assert hash(player1) == hash(player2)