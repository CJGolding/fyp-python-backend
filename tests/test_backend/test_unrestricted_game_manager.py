import pytest

from backend import UnrestrictedGameManager, Recorder


def test_when_instantiating_with_no_parameters_then_use_default_values() -> None:
    game_manager = UnrestrictedGameManager()

    assert game_manager.team_size == 2
    assert game_manager.p_norm == 1.0
    assert game_manager.q_norm == 1.0
    assert game_manager.fairness_weight == 0.1
    assert game_manager.recorder is None
    assert game_manager.skill_window == 18

def test_when_instantiating_with_parameters_then_use_provided_values() -> None:
    game_manager = UnrestrictedGameManager(team_size=3, p_norm=2.0, q_norm=3.0, fairness_weight=0.5,
                                           is_recording=True, approximate=True)

    assert game_manager.team_size == 3
    assert game_manager.p_norm == 2.0
    assert game_manager.q_norm == 3.0
    assert game_manager.fairness_weight == 0.5
    assert isinstance(game_manager.recorder, Recorder)
    assert game_manager.skill_window == 5

def test_when_invalid_team_size_then_raise_value_error() -> None:
    with pytest.raises(ValueError) as e:
        UnrestrictedGameManager(team_size=6)

    assert str(e.value) == "Invalid value for team_size: 6. Must be between 1 and 5."

def test_when_invalid_p_norm_then_raise_value_error() -> None:
    with pytest.raises(ValueError) as e:
        UnrestrictedGameManager(p_norm=0.5)

    assert str(e.value) == "Invalid value for p_norm: 0.5. Must be greater than or equal to 1."

def test_when_invalid_q_norm_then_raise_value_error() -> None:
    with pytest.raises(ValueError) as e:
        UnrestrictedGameManager(q_norm=0.5)

    assert str(e.value) == "Invalid value for q_norm: 0.5. Must be greater than or equal to 1."

def test_when_invalid_fairness_weight_then_raise_value_error() -> None:
    with pytest.raises(ValueError) as e:
        UnrestrictedGameManager(fairness_weight=0.0)

    assert str(e.value) == "Invalid value for fairness_weight: 0.0. Must be greater than 0."

def test_when_creating_candidate_game_then_imbalance_is_not_none() -> None:
    game_manager = UnrestrictedGameManager()
    from backend.player import Player
    player = Player(id=1, skill=100)
    team_x = {Player(id=1, skill=100)}
    team_y = {Player(id=2, skill=150)}

    candidate_game = game_manager._create_candidate_game(player, team_x, team_y)

    assert candidate_game.imbalance is not None
    assert candidate_game.priority is None

