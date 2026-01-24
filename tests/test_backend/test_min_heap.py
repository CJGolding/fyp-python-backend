from backend import MinHeap, Player, CandidateGame

def test_when_change_then_heap_size_changes_and_invariant_maintained() -> None:
    heap = MinHeap()

    player1 = Player(id=1, skill=100)
    player2 = Player(id=2, skill=150)
    player3 = Player(id=3, skill=200)
    player4 = Player(id=4, skill=300)
    candidate_game1 = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)
    candidate_game2 = CandidateGame(anchor_player=player3, team_x={player3}, team_y={player4}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)

    heap.push(candidate_game2)
    heap.push(candidate_game1)
    assert len(heap) == 2

    min_game = heap.peek()
    assert min_game == candidate_game1
    heap.remove(1)
    assert len(heap) == 1

    min_game = heap.peek()
    assert min_game == candidate_game2
    heap.remove(3)
    assert len(heap) == 0

def test_when_removing_invalid_game_from_heap_then_no_error_is_raised() -> None:
    heap = MinHeap()

    player1 = Player(id=1, skill=100)
    player2 = Player(id=2, skill=150)
    candidate_game = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)

    heap.push(candidate_game)
    assert len(heap) == 1

    heap.remove(3)
    assert len(heap) == 1


def test_when_game_already_in_heap_then_value_is_updated() -> None:
    heap = MinHeap()

    player1 = Player(id=1, skill=100)
    player2 = Player(id=2, skill=150)
    candidate_game = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)

    heap.push(candidate_game)
    assert len(heap) == 1

    updated_candidate_game = CandidateGame(anchor_player=player1, team_x={player1}, team_y={player2}, p_norm=2.0, q_norm=2.0, fairness_weight=0.2)
    heap.push(updated_candidate_game)
    assert len(heap) == 1
