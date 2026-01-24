from backend import TimeSensitiveGameManager, Recorder

def test_when_instantiating_with_no_parameters_then_use_default_values() -> None:
    game_manager = TimeSensitiveGameManager()

    assert game_manager.team_size == 2
    assert game_manager.p_norm == 1.0
    assert game_manager.q_norm == 1.0
    assert game_manager.fairness_weight == 0.1
    assert game_manager.queue_weight == 0.1
    assert game_manager.recorder is None
    assert game_manager.skill_window == 18

def test_when_instantiating_with_parameters_then_use_provided_values() -> None:
    game_manager = TimeSensitiveGameManager(team_size=3, p_norm=2.0, q_norm=3.0, fairness_weight=0.5,
                                           queue_weight=0.2, is_recording=True, approximate=True)

    assert game_manager.team_size == 3
    assert game_manager.p_norm == 2.0
    assert game_manager.q_norm == 3.0
    assert game_manager.fairness_weight == 0.5
    assert game_manager.queue_weight == 0.2
    assert isinstance(game_manager.recorder, Recorder)
    assert game_manager.skill_window == 5

def test_when_creating_candidate_game_then_priority_is_not_none() -> None:
    game_manager = TimeSensitiveGameManager()
    from backend.player import Player
    player = Player(id=1, skill=100)
    team_x = {Player(id=1, skill=100)}
    team_y = {Player(id=2, skill=150)}

    candidate_game = game_manager._create_candidate_game(player, team_x, team_y)

    assert candidate_game.priority is not None