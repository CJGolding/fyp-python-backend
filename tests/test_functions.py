from common.functions import (
    team_p_skill,
    p_fairness,
    mean_skill,
    q_uniformity,
    imbalance,
    priority
)
from tests.mock_classes import MockPlayer


class TestTeamPSkill:

    def test_when_calculating_with_p_equals_1_then_returns_sum_of_skills(self):
        team = frozenset([MockPlayer(1, 100), MockPlayer(2, 200), MockPlayer(3, 300)])
        result = team_p_skill(team, p_norm=1.0)
        assert result == 600.0

    def test_when_calculating_with_p_equals_2_then_returns_euclidean_norm(self):
        team = frozenset([MockPlayer(1, 3), MockPlayer(2, 4)])
        result = team_p_skill(team, p_norm=2.0)
        assert abs(result - 5.0) < 0.001

    def test_when_calculating_with_p_equals_infinity_then_returns_max_skill(self):
        team = frozenset([MockPlayer(1, 100), MockPlayer(2, 500), MockPlayer(3, 200)])
        result = team_p_skill(team, p_norm=float('inf'))
        assert result == 500.0

    def test_when_team_has_single_player_then_returns_player_skill(self):
        team = frozenset([MockPlayer(1, 250)])
        result = team_p_skill(team, p_norm=2.0)
        assert result == 250.0

    def test_when_using_high_p_norm_then_biased_towards_high_skill(self):
        team = frozenset([MockPlayer(1, 1), MockPlayer(2, 10)])
        result_p2 = team_p_skill(team, p_norm=2.0)
        result_p5 = team_p_skill(team, p_norm=5.0)
        assert result_p5 < result_p2
        assert result_p5 > 10.0


class TestPFairness:

    def test_when_teams_have_equal_skill_then_returns_zero(self):
        team_x = frozenset([MockPlayer(1, 100), MockPlayer(2, 100)])
        team_y = frozenset([MockPlayer(3, 100), MockPlayer(4, 100)])
        result = p_fairness(team_x, team_y, p_norm=1.0)
        assert result == 0.0

    def test_when_calculating_with_p_equals_1_then_uses_sum_difference(self):
        team_x = frozenset([MockPlayer(1, 100), MockPlayer(2, 200)])
        team_y = frozenset([MockPlayer(3, 150), MockPlayer(4, 250)])
        result = p_fairness(team_x, team_y, p_norm=1.0)
        assert result == 100.0

    def test_when_calculating_with_p_equals_2_then_uses_euclidean_difference(self):
        team_x = frozenset([MockPlayer(1, 3), MockPlayer(2, 4)])
        team_y = frozenset([MockPlayer(3, 6), MockPlayer(4, 8)])
        result = p_fairness(team_x, team_y, p_norm=2.0)
        assert abs(result - 5.0) == 0.0

    def test_when_calculating_with_p_equals_infinity_then_uses_max_difference(self):
        team_x = frozenset([MockPlayer(1, 100), MockPlayer(2, 200)])
        team_y = frozenset([MockPlayer(3, 150), MockPlayer(4, 300)])
        result = p_fairness(team_x, team_y, p_norm=float('inf'))
        assert result == 100.0

    def test_when_teams_have_different_strength_then_returns_absolute_difference(self):
        team_x = frozenset([MockPlayer(1, 500)])
        team_y = frozenset([MockPlayer(2, 200)])
        result = p_fairness(team_x, team_y, p_norm=1.0)
        assert result == 300.0


class TestMeanSkill:

    def test_when_calculating_mean_of_equal_skills_then_returns_skill_value(self):
        players = frozenset([MockPlayer(1, 100), MockPlayer(2, 100), MockPlayer(3, 100)])
        result = mean_skill(players)
        assert result == 100.0

    def test_when_calculating_mean_then_returns_average(self):
        players = frozenset([MockPlayer(1, 100), MockPlayer(2, 200), MockPlayer(3, 300)])
        result = mean_skill(players)
        assert result == 200.0

    def test_when_single_player_then_returns_player_skill(self):
        players = frozenset([MockPlayer(1, 250)])
        result = mean_skill(players)
        assert result == 250.0


class TestQUniformity:

    def test_when_all_players_same_skill_then_returns_zero(self):
        players = {MockPlayer(1, 100), MockPlayer(2, 100), MockPlayer(3, 100)}
        result = q_uniformity(players, q_norm=2.0)
        assert abs(result) == 0.0

    def test_when_calculating_with_q_equals_2_then_returns_standard_deviation(self):
        players = {MockPlayer(1, 90), MockPlayer(2, 100), MockPlayer(3, 110)}
        result = q_uniformity(players, q_norm=2.0)
        expected = ((1.0 / 3.0) * (10 ** 2 + 0 ** 2 + 10 ** 2)) ** 0.5
        assert abs(result - expected) == 0.0

    def test_when_calculating_with_q_equals_1_then_returns_average_deviation(self):
        players = {MockPlayer(1, 80), MockPlayer(2, 100), MockPlayer(3, 120)}
        result = q_uniformity(players, q_norm=1.0)
        expected = (1.0 / 3.0) * (20 + 0 + 20)
        assert abs(result - expected) == 0.0

    def test_when_calculating_with_q_equals_infinity_then_returns_max_deviation(self):
        players = {MockPlayer(1, 50), MockPlayer(2, 100), MockPlayer(3, 120)}
        result = q_uniformity(players, q_norm=float('inf'))
        mean = 90.0
        expected = max(abs(50.0 - mean), abs(100.0 - mean), abs(120.0 - mean))
        assert abs(result - expected) == 0.0

    def test_when_single_outlier_then_high_q_norm_more_sensitive(self):
        players = {MockPlayer(1, 100), MockPlayer(2, 100), MockPlayer(3, 110)}
        result_q1 = q_uniformity(players, q_norm=1.0)
        result_q5 = q_uniformity(players, q_norm=5.0)
        assert result_q5 > result_q1


class TestImbalance:

    def test_when_perfectly_balanced_teams_then_returns_only_uniformity(self):
        team_x = frozenset([MockPlayer(1, 100), MockPlayer(2, 100)])
        team_y = frozenset([MockPlayer(3, 100), MockPlayer(4, 100)])
        result = imbalance(team_x, team_y, p_norm=1.0, q_norm=2.0, fairness_weight=1.0)
        assert abs(result) == 0.0

    def test_when_calculating_imbalance_then_combines_fairness_and_uniformity(self):
        team_x = frozenset([MockPlayer(1, 100)])
        team_y = frozenset([MockPlayer(2, 200)])
        result = imbalance(team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=0.5)
        expected_fairness = 100.0
        expected_uniformity = 50.0
        expected = 0.5 * expected_fairness + expected_uniformity
        assert abs(result - expected) == 0.0

    def test_when_fairness_weight_is_zero_then_returns_only_uniformity(self):
        team_x = frozenset([MockPlayer(1, 100)])
        team_y = frozenset([MockPlayer(2, 500)])
        result = imbalance(team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=0.0)
        expected_uniformity = q_uniformity(team_x | team_y, 1.0)
        assert abs(result - expected_uniformity) == 0.0

    def test_when_fairness_weight_is_high_then_fairness_dominates(self):
        team_x = frozenset([MockPlayer(1, 100)])
        team_y = frozenset([MockPlayer(2, 200)])
        result_low = imbalance(team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=0.1)
        result_high = imbalance(team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=10.0)
        assert result_high > result_low * 15

    def test_when_using_different_norms_then_results_vary(self):
        team_x = frozenset([MockPlayer(1, 100), MockPlayer(2, 200)])
        team_y = frozenset([MockPlayer(3, 150), MockPlayer(4, 250)])
        result_p1_q1 = imbalance(team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=1.0)
        result_p2_q2 = imbalance(team_x, team_y, p_norm=2.0, q_norm=2.0, fairness_weight=1.0)
        result_pinf_qinf = imbalance(team_x, team_y, p_norm=float('inf'), q_norm=float('inf'),
                                     fairness_weight=1.0)
        assert result_p1_q1 != result_p2_q2
        assert result_p2_q2 != result_pinf_qinf

    def test_when_real_world_scenario_then_calculates_correctly(self):
        team_x = frozenset([MockPlayer(1, 1200), MockPlayer(2, 1400)])
        team_y = frozenset([MockPlayer(3, 1250), MockPlayer(4, 1350)])
        result = imbalance(team_x, team_y, p_norm=1.0, q_norm=2.0, fairness_weight=0.5)
        assert result >= 0


class TestPriority:

    def test_when_calculating_priority_then_combines_imbalance_and_wait_time(self):
        team_x = frozenset([MockPlayer(1, 100, enqueue_time=5.0)])
        team_y = frozenset([MockPlayer(2, 100, enqueue_time=10.0)])
        imbalance_value = 50.0
        queue_weight = 2.0
        result = priority(team_x, team_y, queue_weight, imbalance_value)
        assert result == 60.0

    def test_when_queue_weight_is_zero_then_returns_only_imbalance(self):
        team_x = frozenset([MockPlayer(1, 100, enqueue_time=100.0)])
        team_y = frozenset([MockPlayer(2, 100, enqueue_time=200.0)])
        imbalance_value = 50.0
        result = priority(team_x, team_y, queue_weight=0.0, imbalance=imbalance_value)
        assert result == 50.0

    def test_when_player_waited_long_then_priority_increases(self):
        team_x = frozenset([MockPlayer(1, 100, enqueue_time=1.0)])
        team_y = frozenset([MockPlayer(2, 100, enqueue_time=100.0)])
        imbalance_value = 50.0
        queue_weight = 1.0
        result = priority(team_x, team_y, queue_weight, imbalance_value)
        assert result == 51.0

    def test_when_high_queue_weight_then_wait_time_matters_more(self):
        team_x = frozenset([MockPlayer(1, 100, enqueue_time=5.0)])
        team_y = frozenset([MockPlayer(2, 100, enqueue_time=10.0)])
        imbalance_value = 50.0
        result_low = priority(team_x, team_y, queue_weight=0.1, imbalance=imbalance_value)
        result_high = priority(team_x, team_y, queue_weight=10.0, imbalance=imbalance_value)
        assert result_high > result_low
        assert abs(result_low - 50.5) == 0.0
        assert abs(result_high - 100.0) == 0.0

    def test_when_multiple_players_then_uses_minimum_enqueue_time(self):
        team_x = frozenset([
            MockPlayer(1, 100, enqueue_time=10.0),
            MockPlayer(2, 100, enqueue_time=3.0),
        ])
        team_y = frozenset([
            MockPlayer(3, 100, enqueue_time=15.0),
            MockPlayer(4, 100, enqueue_time=20.0),
        ])
        result = priority(team_x, team_y, queue_weight=1.0, imbalance=0.0)
        assert result == 3.0

    def test_when_all_players_same_enqueue_time_then_uses_that_value(self):
        team_x = frozenset([MockPlayer(1, 100, enqueue_time=7.5)])
        team_y = frozenset([MockPlayer(2, 100, enqueue_time=7.5)])
        result = priority(team_x, team_y, queue_weight=2.0, imbalance=10.0)
        assert result == 25.0


class TestFunctionsEdgeCases:

    def test_when_calculating_with_very_high_skills_then_handles_correctly(self):
        team_x = frozenset([MockPlayer(1, 10000)])
        team_y = frozenset([MockPlayer(2, 10000)])
        result = p_fairness(team_x, team_y, p_norm=1.0)
        assert result == 0.0

    def test_when_using_fractional_p_norm_then_calculates_correctly(self):
        team = frozenset([MockPlayer(1, 16)])
        result = team_p_skill(team, p_norm=0.5)
        assert abs(result - 16.0) == 0.0

    def test_when_mix_of_zero_and_nonzero_skills_then_calculates(self):
        team_x = frozenset([MockPlayer(1, 0), MockPlayer(2, 100)])
        team_y = frozenset([MockPlayer(3, 50), MockPlayer(4, 50)])
        result = p_fairness(team_x, team_y, p_norm=1.0)
        assert result == 0.0


class TestFunctionsIntegration:

    def test_when_building_complete_matchmaking_score_then_consistent(self):
        team_x = frozenset([MockPlayer(1, 1000, enqueue_time=5.0)])
        team_y = frozenset([MockPlayer(2, 1100, enqueue_time=10.0)])
        fairness = p_fairness(team_x, team_y, p_norm=1.0)
        uniformity = q_uniformity(team_x | team_y, q_norm=1.0)
        imbalance_score = imbalance(team_x, team_y, p_norm=1.0, q_norm=1.0, fairness_weight=1.0)
        priority_score = priority(team_x, team_y, queue_weight=1.0, imbalance=imbalance_score)
        assert fairness == 100.0
        assert uniformity == 50.0
        assert imbalance_score == fairness + uniformity
        assert priority_score == imbalance_score + 5.0

    def test_when_comparing_perfect_vs_imperfect_match_then_scores_differ(self):
        perfect_x = frozenset([MockPlayer(1, 100), MockPlayer(2, 100)])
        perfect_y = frozenset([MockPlayer(3, 100), MockPlayer(4, 100)])
        imperfect_x = frozenset([MockPlayer(5, 50), MockPlayer(6, 150)])
        imperfect_y = frozenset([MockPlayer(7, 75), MockPlayer(8, 125)])
        perfect_score = imbalance(perfect_x, perfect_y, p_norm=2.0, q_norm=2.0, fairness_weight=1.0)
        imperfect_score = imbalance(imperfect_x, imperfect_y, p_norm=2.0, q_norm=2.0, fairness_weight=1.0)
        assert perfect_score < imperfect_score

    def test_when_using_paper_formulas_then_matches_expectations(self):
        team_x = frozenset([MockPlayer(1, 1000), MockPlayer(2, 1200)])
        team_y = frozenset([MockPlayer(3, 1050), MockPlayer(4, 1150)])
        result = imbalance(team_x, team_y, p_norm=1.0, q_norm=2.0, fairness_weight=0.1)
        assert result >= 0
        assert result < 100
