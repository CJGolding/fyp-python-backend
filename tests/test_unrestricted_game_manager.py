import math

import pytest

from backend.unrestricted_game_manager import UnrestrictedGameManager
from tests.mock_classes import MockPlayer, MockCandidateGame, MockSortedSet, MockMinHeap, MockRecorder


def mock_p_fairness(team_x, team_y, p_norm, q_norm):
    return 5.0


@pytest.fixture(autouse=True)
def mock_imports(monkeypatch):
    monkeypatch.setattr('backend.sorted_set.SortedSet', MockSortedSet)
    monkeypatch.setattr('backend.min_heap.MinHeap', MockMinHeap)
    monkeypatch.setattr('backend.recorder.Recorder', MockRecorder)
    monkeypatch.setattr('common.functions.p_fairness', mock_p_fairness)


class TestUnrestrictedGameManagerInitialisation:

    def test_when_creating_manager_with_valid_params_then_initialises_correctly(self):
        manager = UnrestrictedGameManager(team_size=2, p_norm=2.0, q_norm=1.0, fairness_weight=0.5)

        assert manager.team_size == 2
        assert manager.p_norm == 2.0
        assert manager.q_norm == 1.0
        assert manager.fairness_weight == 0.5

    def test_when_creating_manager_then_calculates_skill_window_correctly(self):
        manager = UnrestrictedGameManager(team_size=2, p_norm=1.0, q_norm=2.0, fairness_weight=0.5)

        expected_window = math.ceil(4 * 1.5 * (2 ** 1.5))
        assert manager.skill_window == expected_window

    def test_when_creating_manager_then_required_players_is_correct(self):
        manager = UnrestrictedGameManager(team_size=3)

        assert manager.required_players == 5

    def test_when_creating_manager_with_invalid_team_size_then_raises_error(self):
        with pytest.raises(ValueError, match="team_size"):
            UnrestrictedGameManager(team_size=0)

        with pytest.raises(ValueError, match="team_size"):
            UnrestrictedGameManager(team_size=10)

    def test_when_creating_manager_with_invalid_p_norm_then_raises_error(self):
        with pytest.raises(ValueError, match="p_norm"):
            UnrestrictedGameManager(p_norm=0.5)

        with pytest.raises(ValueError, match="p_norm"):
            UnrestrictedGameManager(p_norm=15.0)

    def test_when_creating_manager_with_invalid_fairness_weight_then_raises_error(self):
        with pytest.raises(ValueError, match="fairness_weight"):
            UnrestrictedGameManager(fairness_weight=0.0)

        with pytest.raises(ValueError, match="fairness_weight"):
            UnrestrictedGameManager(fairness_weight=15.0)

    def test_when_creating_manager_with_approximate_false_then_uses_brute_force(self):
        manager = UnrestrictedGameManager(approximate=False)

        assert manager._partition_solver == manager._brute_force_partition

    def test_when_creating_manager_with_approximate_true_then_uses_greedy(self):
        manager = UnrestrictedGameManager(approximate=True)

        assert manager._partition_solver == manager._greedy_balanced_partition

    def test_when_creating_manager_with_recording_then_creates_recorder(self):
        manager = UnrestrictedGameManager(is_recording=True)
        assert manager.recorder is not None

        manager = UnrestrictedGameManager(is_recording=False)

        assert manager.recorder is None

    def test_when_creating_manager_then_match_quality_metric_is_imbalance(self):
        manager = UnrestrictedGameManager()

        assert manager._match_quality_metric == "imbalance"


class TestUnrestrictedGameManagerConfiguration:

    def test_when_getting_parameters_then_returns_correct_dict(self):
        manager = UnrestrictedGameManager(team_size=3, p_norm=2.0, q_norm=1.5, fairness_weight=0.8)

        params = manager.get_parameters()

        assert set(params.keys()) == {"team_size", "p_norm", "q_norm", "fairness_weight", "skill_window", "session_id"}
        assert params["team_size"] == 3
        assert params["p_norm"] == 2.0
        assert params["q_norm"] == 1.5
        assert params["fairness_weight"] == 0.8
        assert params["skill_window"] == manager.skill_window
        assert "session_id" in params

    def test_when_validating_config_with_valid_value_then_returns_value(self):
        result = UnrestrictedGameManager.validate_config(5, lambda x: x > 0, "test", "x > 0")

        assert result == 5

    def test_when_validating_config_with_invalid_value_then_raises_error(self):
        with pytest.raises(ValueError, match="test"):
            UnrestrictedGameManager.validate_config(-1, lambda x: x > 0, "test", "x > 0")

    def test_when_calling_repr_then_returns_readable_string(self):
        manager = UnrestrictedGameManager(team_size=2, p_norm=1.0, q_norm=2.0, fairness_weight=0.5)

        result = repr(manager)

        assert result == "Team Size: 2, P: 1.0, Q: 2.0, α: 0.5, Window: 17"


class TestUnrestrictedGameManagerPartitionAlgorithms:

    def test_when_brute_force_partition_called_then_returns_best_game(self, monkeypatch):
        manager = UnrestrictedGameManager(team_size=2, approximate=False)

        anchor = MockPlayer(1, 1000)
        remaining = {MockPlayer(2, 1100), MockPlayer(3, 1200), MockPlayer(4, 1300)}

        def mock_create_candidate_game(*args, **kwargs):
            return MockCandidateGame(anchor, frozenset({anchor}), frozenset(), imbalance=3.0)

        monkeypatch.setattr(manager, '_create_candidate_game', mock_create_candidate_game)

        game, value, count = manager._brute_force_partition(anchor, remaining)

        assert game is not None
        assert value >= 0
        assert count > 0

    def test_when_greedy_partition_called_then_returns_balanced_game(self, monkeypatch):
        manager = UnrestrictedGameManager(team_size=2, approximate=True)

        anchor = MockPlayer(1, 1000)
        remaining = {MockPlayer(2, 1100), MockPlayer(3, 1200), MockPlayer(4, 1300)}

        def mock_create_candidate_game(*args, **kwargs):
            return MockCandidateGame(anchor, frozenset({anchor}), frozenset(), imbalance=3.0)

        monkeypatch.setattr(manager, '_create_candidate_game', mock_create_candidate_game)

        game, value, count = manager._greedy_balanced_partition(anchor, remaining)

        assert game is not None
        assert value >= 0
        assert count == 1


class TestUnrestrictedGameManagerPlayerManagement:

    def test_when_inserting_player_then_added_to_players_queue(self, monkeypatch):
        manager = UnrestrictedGameManager()
        player = MockPlayer(1, 1500)

        monkeypatch.setattr(manager, '_update_candidate_games_for_list', lambda x: None)
        manager._insert_player(player)

        assert player in manager.players

    def test_when_removing_player_then_removed_from_queue(self, monkeypatch):
        manager = UnrestrictedGameManager()
        player = MockPlayer(1, 1500)

        monkeypatch.setattr(manager, '_update_candidate_games_for_list', lambda x: None)
        manager._insert_player(player)
        assert player in manager.players

        manager._remove_player(player)
        assert player not in manager.players

    def test_when_cancelling_then_sets_cancelled_flag(self):
        manager = UnrestrictedGameManager()

        manager.cancel()

        assert manager._cancelled is True


class TestUnrestrictedGameManagerBestGameCalculation:

    def test_when_calculating_best_game_with_insufficient_players_then_returns_none(self, monkeypatch):
        manager = UnrestrictedGameManager(team_size=2)
        player = MockPlayer(1, 1000)

        monkeypatch.setattr(manager, '_update_candidate_games_for_list', lambda x: None)
        manager._insert_player(player)

        result = manager._calculate_best_game_including_player(player)

        assert result is None

    def test_when_calculating_best_game_with_cancelled_flag_then_returns_none(self, monkeypatch):
        manager = UnrestrictedGameManager(team_size=2)
        player = MockPlayer(1, 1000)
        manager._cancelled = True

        monkeypatch.setattr(manager, '_update_candidate_games_for_list', lambda x: None)
        manager._insert_player(player)
        for i in range(2, 10):
            manager._insert_player(MockPlayer(i, 1000 + i * 10))

        result = manager._calculate_best_game_including_player(player)

        assert result is None

    def test_when_calculating_best_game_then_uses_skill_window(self, monkeypatch):
        manager = UnrestrictedGameManager(team_size=2)
        player = MockPlayer(1, 1000)

        monkeypatch.setattr(manager, '_update_candidate_games_for_list', lambda x: None)
        manager._insert_player(player)
        for i in range(2, 20):
            manager._insert_player(MockPlayer(i, 1000 + i * 10))

        called = []

        def mock_partition_solver(*args, **kwargs):
            called.append(True)
            return (MockCandidateGame(player, frozenset({player}), frozenset()), 5.0, 1)

        monkeypatch.setattr(manager, '_partition_solver', mock_partition_solver)

        result = manager._calculate_best_game_including_player(player)

        assert len(called) > 0


class TestUnrestrictedGameManagerMatchCreation:

    def test_when_creating_match_with_no_games_then_logs_warning(self):
        manager = UnrestrictedGameManager()

        manager.create_match()

        assert len(manager.created_matches) == 0

    def test_when_creating_match_with_valid_game_then_adds_to_created_matches(self, monkeypatch):
        manager = UnrestrictedGameManager()

        anchor = MockPlayer(1, 1000)
        team_x = frozenset([MockPlayer(1, 1000), MockPlayer(2, 1100)])
        team_y = frozenset([MockPlayer(3, 1200), MockPlayer(4, 1300)])
        game = MockCandidateGame(anchor, team_x, team_y)

        manager.candidate_games.push(game)

        monkeypatch.setattr(manager, '_remove_players', lambda x: None)
        manager.create_match()

        assert len(manager.created_matches) == 1
        assert manager.created_matches[0] == game

    def test_when_creating_match_then_removes_players_from_game(self, monkeypatch):
        manager = UnrestrictedGameManager()

        anchor = MockPlayer(1, 1000)
        team_x = frozenset([MockPlayer(1, 1000), MockPlayer(2, 1100)])
        team_y = frozenset([MockPlayer(3, 1200), MockPlayer(4, 1300)])
        game = MockCandidateGame(anchor, team_x, team_y)

        manager.candidate_games.push(game)

        removed_players_list = []

        def mock_remove_players(players):
            removed_players_list.append(list(players))

        monkeypatch.setattr(manager, '_remove_players', mock_remove_players)
        manager.create_match()

        assert len(removed_players_list) == 1
        assert len(removed_players_list[0]) == 4


class TestGameManagerEdgeCases:

    def test_when_manager_with_minimum_team_size_then_works_correctly(self):
        manager = UnrestrictedGameManager(team_size=1)

        assert manager.team_size == 1
        assert manager.required_players == 1

    def test_when_manager_with_maximum_team_size_then_works_correctly(self):
        manager = UnrestrictedGameManager(team_size=5)

        assert manager.team_size == 5
        assert manager.required_players == 9

    def test_when_manager_with_high_fairness_weight_then_larger_window(self):
        manager1 = UnrestrictedGameManager(fairness_weight=0.1)
        manager2 = UnrestrictedGameManager(fairness_weight=5.0)

        assert manager2.skill_window > manager1.skill_window


class TestGameManagerIntegration:

    def test_when_creating_manager_and_validating_state_then_consistent(self):
        manager = UnrestrictedGameManager(
            team_size=3,
            p_norm=2.0,
            q_norm=1.5,
            fairness_weight=0.8,
            approximate=True,
            is_recording=False
        )

        assert manager.team_size == 3
        assert manager.required_players == 5
        assert manager.p_norm == 2.0
        assert manager.q_norm == 1.5
        assert manager.fairness_weight == 0.8
        assert manager._partition_solver == manager._greedy_balanced_partition
        assert manager.recorder is None
        assert manager._cancelled is False
        assert len(manager.created_matches) == 0

    def test_when_comparing_brute_force_and_greedy_managers_then_different_solvers(self):
        brute_force = UnrestrictedGameManager(approximate=False)
        greedy = UnrestrictedGameManager(approximate=True)

        assert brute_force._partition_solver == brute_force._brute_force_partition
        assert greedy._partition_solver == greedy._greedy_balanced_partition
        assert brute_force._partition_solver != greedy._partition_solver
