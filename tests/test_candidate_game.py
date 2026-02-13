import pytest

from backend.candidate_game import CandidateGame
from tests.mock_classes import MockPlayer

MOCK_IMBALANCE_VALUE = 10.0
MOCK_PRIORITY_VALUE = 25.0


def mock_imbalance(team_x, team_y, p_norm, q_norm, fairness_weight):
    return MOCK_IMBALANCE_VALUE


def mock_priority(team_x, team_y, queue_weight, imbalance):
    if queue_weight is None:
        return None
    return MOCK_PRIORITY_VALUE


@pytest.fixture(autouse=True)
def mock_imports(monkeypatch):
    import backend.candidate_game

    monkeypatch.setattr(backend.candidate_game, 'imbalance', mock_imbalance)
    monkeypatch.setattr(backend.candidate_game, 'priority', mock_priority)


class TestCandidateGameInitialisation:

    def test_when_creating_candidate_game_then_properties_are_set(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0, fairness_weight=0.5)

        assert game.anchor_player == anchor
        assert game.anchor_player.id == 1
        assert game.team_x == team_x
        assert game.team_y == team_y
        assert game.imbalance == 10.0

    def test_when_creating_with_queue_weight_then_priority_is_calculated(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                             fairness_weight=0.5, queue_weight=1.5)

        assert game.priority == 25.0

    def test_when_creating_without_queue_weight_then_priority_is_none(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0, fairness_weight=0.5)

        assert game.priority is None


class TestCandidateGameToDict:

    def test_when_converting_to_dict_then_contains_all_expected_keys(self):
        anchor = MockPlayer(123)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                             fairness_weight=0.5, queue_weight=1.5)
        result = game.to_dict()

        expected_keys = {"anchor_player_id", "team_x", "team_y", "imbalance", "priority"}
        assert set(result.keys()) == expected_keys
        assert result["anchor_player_id"] == 123
        assert set(result["team_x"]) == {1, 2}
        assert set(result["team_y"]) == {3, 4}
        assert result["imbalance"] == 10.0
        assert result["priority"] == 25.0

    def test_when_converting_to_dict_without_priority_then_priority_is_none(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=0.5)
        result = game.to_dict()

        assert result["priority"] is None


class TestCandidateGameComparison:

    def test_when_both_have_priority_then_compares_by_priority(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game1 = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                              fairness_weight=0.5, queue_weight=1.0)
        game2 = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                              fairness_weight=0.5, queue_weight=2.0)

        assert not (game1 < game2)
        assert game1.priority == game2.priority == 25.0

    def test_when_neither_has_priority_then_compares_by_imbalance(self):
        anchor = MockPlayer(1)
        team_x1 = frozenset([MockPlayer(1)])
        team_y1 = frozenset([MockPlayer(2)])
        team_x2 = frozenset([MockPlayer(1), MockPlayer(2), MockPlayer(3)])
        team_y2 = frozenset([MockPlayer(4)])

        game1 = CandidateGame(anchor, team_x1, team_y1, p_norm=1.0, q_norm=1.0, fairness_weight=0.0)
        game2 = CandidateGame(anchor, team_x2, team_y2, p_norm=1.0, q_norm=1.0, fairness_weight=0.0)

        assert not (game1 < game2)
        assert game1.imbalance == game2.imbalance == 10.0


class TestCandidateGameStr:

    def test_when_converting_to_string_then_contains_all_components(self):
        anchor = MockPlayer(123)
        team_x = frozenset([MockPlayer(10), MockPlayer(20)])
        team_y = frozenset([MockPlayer(30), MockPlayer(40)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0, fairness_weight=0.5)
        result = str(game)

        assert result == "CandidateGame(Anchor Player ID: 123, Team X: [10, 20], Team Y: [40, 30], f: 10.0)"

    def test_when_game_has_priority_then_string_contains_priority(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                             fairness_weight=0.5, queue_weight=1.5)
        result = str(game)

        assert result == "CandidateGame(Anchor Player ID: 1, Team X: [1, 2], Team Y: [3, 4], f: 10.0, g: 25.0)"


class TestCandidateGameEdgeCases:

    def test_when_teams_have_many_players_then_works_correctly(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(i) for i in range(1, 100)])
        team_y = frozenset([MockPlayer(i) for i in range(100, 200)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=0.0)

        assert game.imbalance == 10.0


class TestCandidateGameIntegration:

    def test_when_comparing_games_with_and_without_priority_then_handles_correctly(self):
        anchor = MockPlayer(1)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game_with_priority = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                                           fairness_weight=0.5, queue_weight=1.0)
        game_without_priority = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                                              fairness_weight=0.5, queue_weight=None)

        assert game_with_priority.imbalance == game_without_priority.imbalance == 10.0
        assert game_with_priority.priority == 25.0
        assert game_without_priority.priority is None

    def test_when_serialising_game_data_then_preserves_information(self):
        anchor = MockPlayer(123)
        team_x = frozenset([MockPlayer(1), MockPlayer(2)])
        team_y = frozenset([MockPlayer(3), MockPlayer(4)])

        game = CandidateGame(anchor, team_x, team_y, p_norm=2.0, q_norm=1.0,
                             fairness_weight=0.5, queue_weight=1.5)
        data = game.to_dict()

        assert data["anchor_player_id"] == 123
        assert set(data["team_x"]) == {1, 2}
        assert set(data["team_y"]) == {3, 4}
        assert data["imbalance"] == 10.0
        assert data["priority"] == 25.0
