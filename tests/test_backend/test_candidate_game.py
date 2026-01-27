from backend import CandidateGame, Player

def test_candidate_game_to_dict() -> None:
    player1 = Player(player_id=1, skill=100)
    player2 = Player(player_id=2, skill=150)
    candidate_game = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)
    game_dict = candidate_game.to_dict()
    assert sorted(list(game_dict.keys())) == sorted(["anchor_player_id", "team_x", "team_y", "imbalance", "priority"])
    assert game_dict["anchor_player_id"] == 1
    assert len(game_dict["team_x"]) == 1
    assert len(game_dict["team_y"]) == 1

def test_when_providing_queue_weight_then_priority_is_computed() -> None:
    player1 = Player(player_id=1, skill=100)
    player2 = Player(player_id=2, skill=150)
    candidate_game = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1, queue_weight=0.05)
    assert candidate_game.priority is not None

def test_when_comparing_games_with_imbalance_then_imbalance_is_used() -> None:
    player1 = Player(player_id=1, skill=100)
    player2 = Player(player_id=2, skill=150)
    candidate_game1 = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)
    candidate_game2 = CandidateGame(anchor_player=player2, team_x={player2}, team_y={player1}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)
    assert (candidate_game1 < candidate_game2) == (candidate_game1.imbalance < candidate_game2.imbalance)

def test_when_comparing_games_with_priority_then_priority_is_used() -> None:
    player1 = Player(player_id=1, skill=100)
    player2 = Player(player_id=2, skill=150)
    candidate_game1 = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1, queue_weight=0.05)
    candidate_game2 = CandidateGame(anchor_player=player2, team_x={player2}, team_y={player1}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1, queue_weight=0.05)
    assert (candidate_game1 < candidate_game2) == (candidate_game1.priority < candidate_game2.priority)