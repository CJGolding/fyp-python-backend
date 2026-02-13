import pytest

from backend.player import Player

_mock_time = [0.0]


def mock_now() -> float:
    return _mock_time[0]


def mock_reset() -> None:
    _mock_time[0] = 0.0


def advance_time(seconds: float) -> None:
    _mock_time[0] += seconds


@pytest.fixture(autouse=True)
def mock_imports(monkeypatch):
    mock_reset()

    import backend.clock

    monkeypatch.setattr(backend.clock, 'now', mock_now)
    monkeypatch.setattr(backend.clock, 'reset', mock_reset)

    yield
    mock_reset()


class TestPlayerInitialisation:

    def test_when_creating_player_then_id_is_set(self):
        player = Player(player_id=123, skill=1500)
        assert player.id == 123

    def test_when_creating_player_then_skill_is_set(self):
        player = Player(player_id=123, skill=1500)
        assert player.skill == 1500

    def test_when_creating_player_then_enqueue_time_is_current_time(self):
        advance_time(5.0)
        player = Player(player_id=123, skill=1500)
        assert player.enqueue_time == 5.0

    def test_when_creating_player_then_dequeue_time_is_none(self):
        player = Player(player_id=123, skill=1500)
        assert player.dequeue_time is None


class TestPlayerWaitTime:

    def test_when_player_not_dequeued_then_wait_time_increases_with_clock(self):
        mock_reset()
        player = Player(player_id=123, skill=1500)
        assert player.wait_time == 0.0

        advance_time(5.0)
        assert player.wait_time == 5.0

        advance_time(3.0)
        assert player.wait_time == 8.0

    def test_when_player_dequeued_then_wait_time_is_frozen(self):
        mock_reset()
        player = Player(player_id=123, skill=1500)

        advance_time(5.0)
        player.mark_as_exited()

        frozen_wait_time = player.wait_time
        assert frozen_wait_time == 5.0

        advance_time(10.0)
        assert player.wait_time == frozen_wait_time
        assert player.wait_time == 5.0


class TestMarkAsExited:

    def test_when_marking_as_exited_then_dequeue_time_is_set(self):
        mock_reset()
        player = Player(player_id=123, skill=1500)
        advance_time(5.0)
        player.mark_as_exited()

        assert player.dequeue_time is not None
        assert player.dequeue_time == 5.0

    def test_when_marking_as_exited_multiple_times_then_uses_first_dequeue_time(self):
        mock_reset()
        player = Player(player_id=123, skill=1500)

        advance_time(5.0)
        player.mark_as_exited()
        first_dequeue_time = player.dequeue_time

        advance_time(10.0)
        player.mark_as_exited()

        assert player.dequeue_time == first_dequeue_time


class TestPlayerToDict:

    def test_when_converting_to_dict_then_returns_all_required_keys(self):
        mock_reset()
        player = Player(player_id=123, skill=1500)
        result = player.to_dict()

        assert set(result.keys()) == {"id", "skill", "enqueue_time", "wait_time"}
        assert result["id"] == 123
        assert result["skill"] == 1500

    def test_when_converting_to_dict_then_values_are_rounded_to_two_decimals(self):
        mock_reset()
        advance_time(1.23456)
        player = Player(player_id=123, skill=1500)
        advance_time(2.78912)

        result = player.to_dict()
        assert result["enqueue_time"] == 1.23
        assert result["wait_time"] == 2.79

    def test_when_player_dequeued_then_to_dict_shows_frozen_wait_time(self):
        mock_reset()
        player = Player(player_id=123, skill=1500)
        advance_time(5.0)
        player.mark_as_exited()

        advance_time(10.0)
        result = player.to_dict()

        assert result["wait_time"] == 5.0


class TestPlayerComparison:

    def test_when_comparing_players_by_skill_then_lower_skill_is_less(self):
        player1 = Player(player_id=1, skill=1000)
        player2 = Player(player_id=2, skill=1500)

        assert player1 < player2
        assert player2 > player1

    def test_when_comparing_players_with_same_skill_then_uses_id_for_tiebreak(self):
        player1 = Player(player_id=1, skill=1000)
        player2 = Player(player_id=2, skill=1000)

        assert player1 < player2
        assert player2 > player1

    def test_when_comparing_players_with_same_skill_and_id_then_not_less_or_greater(self):
        player1 = Player(player_id=1, skill=1000)
        player2 = Player(player_id=1, skill=1000)

        assert not (player1 < player2)
        assert not (player1 > player2)

    def test_when_sorting_players_then_sorted_by_skill_then_id(self):
        players = [
            Player(player_id=3, skill=1500),
            Player(player_id=1, skill=1000),
            Player(player_id=2, skill=1000),
            Player(player_id=4, skill=1200),
        ]

        sorted_players = sorted(players)

        assert sorted_players[0].id == 1
        assert sorted_players[1].id == 2
        assert sorted_players[2].id == 4
        assert sorted_players[3].id == 3


class TestPlayerEqualityAndHashing:

    def test_when_players_have_same_id_then_are_equal(self):
        player1 = Player(player_id=123, skill=1000)
        player2 = Player(player_id=123, skill=1500)

        assert player1 == player2

    def test_when_players_have_different_ids_then_are_not_equal(self):
        player1 = Player(player_id=123, skill=1000)
        player2 = Player(player_id=456, skill=1000)

        assert player1 != player2

    def test_when_players_have_same_id_then_have_same_hash(self):
        player1 = Player(player_id=123, skill=1000)
        player2 = Player(player_id=123, skill=1500)

        assert hash(player1) == hash(player2)

    def test_when_using_players_in_set_then_uniqueness_by_id(self):
        player1 = Player(player_id=123, skill=1000)
        player2 = Player(player_id=123, skill=1500)
        player3 = Player(player_id=456, skill=1000)

        players_set = {player1, player2, player3}

        assert len(players_set) == 2

    def test_when_using_players_as_dict_keys_then_keyed_by_id(self):
        player1 = Player(player_id=123, skill=1000)
        player2 = Player(player_id=123, skill=1500)

        player_dict = {}
        player_dict[player1] = "first"
        player_dict[player2] = "second"

        assert len(player_dict) == 1
        assert player_dict[player1] == "second"


class TestPlayerEdgeCases:

    def test_when_player_has_zero_skill_then_works_correctly(self):
        player = Player(player_id=1, skill=0)
        assert player.skill == 0

    def test_when_player_has_very_high_skill_then_works_correctly(self):
        player = Player(player_id=1, skill=10000000)
        assert player.skill == 10000000

    def test_when_multiple_players_created_rapidly_then_enqueue_times_increase(self):
        mock_reset()
        players = []

        for i in range(5):
            players.append(Player(player_id=i, skill=1000))
            advance_time(0.1)

        for i in range(1, 5):
            assert players[i].enqueue_time > players[i - 1].enqueue_time


class TestPlayerIntegration:

    def test_when_multiple_players_in_queue_then_each_tracks_own_time(self):
        mock_reset()

        player1 = Player(player_id=1, skill=1000)
        advance_time(2.0)

        player2 = Player(player_id=2, skill=1000)
        advance_time(3.0)

        assert player1.wait_time == 5.0
        assert player2.wait_time == 3.0

        player1.mark_as_exited()
        advance_time(2.0)

        assert player1.wait_time == 5.0
        assert player2.wait_time == 5.0

    def test_when_creating_and_sorting_diverse_players_then_order_is_correct(self):
        mock_reset()

        players = [
            Player(player_id=5, skill=1500),
            Player(player_id=3, skill=1000),
            Player(player_id=1, skill=1000),
            Player(player_id=4, skill=2000),
            Player(player_id=2, skill=1000),
        ]

        sorted_players = sorted(players)

        expected_ids = [1, 2, 3, 5, 4]
        actual_ids = [p.id for p in sorted_players]

        assert actual_ids == expected_ids
