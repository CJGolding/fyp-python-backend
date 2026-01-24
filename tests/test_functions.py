import pytest

from common.functions import team_p_skill, p_fairness, mean_skill, q_uniformity, imbalance, priority
from backend.player import Player

def test_team_p_skill():
    players = {Player(id=1, skill=10), Player(id=2, skill=20), Player(id=3, skill=30)}
    assert team_p_skill(players, 1) == pytest.approx(60)
    assert team_p_skill(players, 2) == pytest.approx((10**2 + 20**2 + 30**2) ** 0.5)
    assert team_p_skill(players, float('inf')) == 30

def test_p_fairness():
    team_x = {Player(id=1, skill=10), Player(id=2, skill=20)}
    team_y = {Player(id=3, skill=30), Player(id=4, skill=40)}
    assert p_fairness(team_x, team_y, 1) == pytest.approx(abs(30 - 70))
    assert p_fairness(team_x, team_y, 2) == pytest.approx(abs((10**2 + 20**2) ** 0.5 - (30**2 + 40**2) ** 0.5))
    assert p_fairness(team_x, team_y, float('inf')) == pytest.approx(abs(20 - 40))

def test_mean_skill():
    players = {Player(id=1, skill=10), Player(id=2, skill=20), Player(id=3, skill=30)}
    assert mean_skill(players) == pytest.approx(20)

def test_q_uniformity():
    players = {Player(id=1, skill=10), Player(id=2, skill=20), Player(id=3, skill=30)}
    assert q_uniformity(players, 1) == pytest.approx((1/3) * (abs(10-20) + abs(20-20) + abs(30-20)))
    assert q_uniformity(players, float('inf')) == pytest.approx(10)

def test_imbalance():
    team_x = {Player(id=1, skill=10), Player(id=2, skill=20)}
    team_y = {Player(id=3, skill=30), Player(id=4, skill=40)}
    fairness_weight = 0.5
    p_norm = 1
    q_norm = 1
    expected_fairness = p_fairness(team_x, team_y, p_norm)
    expected_uniformity = q_uniformity(team_x | team_y, q_norm)
    expected_imbalance = fairness_weight * expected_fairness + expected_uniformity
    assert imbalance(team_x, team_y, p_norm, q_norm, fairness_weight) == pytest.approx(expected_imbalance)

def test_priority():
    team_x = {Player(id=1, skill=10), Player(id=2, skill=20)}
    team_y = {Player(id=3, skill=30), Player(id=4, skill=40)}
    imbalance_value = 15.0
    min_enqueue_time = list(team_x)[0].enqueue_time
    queue_weight = 0.1
    expected_priority = queue_weight * min_enqueue_time + imbalance_value
    assert priority(team_x, team_y, queue_weight, imbalance_value) == pytest.approx(expected_priority)