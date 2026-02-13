import pytest

from backend.time_sensitive_game_manager import TimeSensitiveGameManager
from backend.unrestricted_game_manager import UnrestrictedGameManager
from tests.mock_classes import MockPlayer


class TestTimeSensitiveGameManagerInitialisation:

    def test_when_creating_time_sensitive_manager_then_extends_unrestricted(self):
        manager = TimeSensitiveGameManager(team_size=2, queue_weight=0.5)

        assert isinstance(manager, UnrestrictedGameManager)
        assert manager.team_size == 2
        assert manager.queue_weight == 0.5

    def test_when_creating_time_sensitive_manager_then_match_quality_is_priority(self):
        manager = TimeSensitiveGameManager(queue_weight=0.5)

        assert manager._match_quality_metric == "priority"

    def test_when_creating_with_invalid_queue_weight_then_raises_error(self):
        with pytest.raises(ValueError, match="queue_weight"):
            TimeSensitiveGameManager(queue_weight=0.0)

        with pytest.raises(ValueError, match="queue_weight"):
            TimeSensitiveGameManager(queue_weight=15.0)

    def test_when_getting_parameters_then_includes_queue_weight(self):
        manager = TimeSensitiveGameManager(team_size=2, queue_weight=1.5)

        params = manager.get_parameters()

        assert params["queue_weight"] == 1.5
        assert params["team_size"] == 2

    def test_when_calling_repr_then_includes_queue_weight(self):
        manager = TimeSensitiveGameManager(queue_weight=1.5, fairness_weight=0.5)

        result = repr(manager)

        assert "β: 1.5" in result
        assert "α: 0.5" in result


class TestTimeSensitiveGameManagerCandidateCreation:

    def test_when_creating_candidate_game_then_includes_queue_weight(self):
        manager = TimeSensitiveGameManager(queue_weight=1.5)

        player = MockPlayer(1, 1000)
        team_x = frozenset([MockPlayer(1, 1000)])
        team_y = frozenset([MockPlayer(2, 1100)])

        game = manager._create_candidate_game(player, team_x, team_y)

        assert game is not None
