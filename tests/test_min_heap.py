import random

import pytest

from backend.min_heap import MinHeap
from tests.mock_classes import MockPlayer, MockCandidateGame


class TestHeapInvariants:

    def _get_heap_array(self, heap: MinHeap) -> list:
        return heap._MinHeap__heap

    def _get_index_map(self, heap: MinHeap) -> dict:
        return heap._MinHeap__index_map

    def _verify_heap_property(self, heap: MinHeap) -> bool:
        heap_array = self._get_heap_array(heap)
        n = len(heap_array)

        for i in range(n):
            left_child = 2 * i + 1
            right_child = 2 * i + 2

            if left_child < n and heap_array[i] > heap_array[left_child]:
                return False
            if right_child < n and heap_array[i] > heap_array[right_child]:
                return False

        return True

    def _verify_index_map_consistency(self, heap: MinHeap) -> bool:
        heap_array = self._get_heap_array(heap)
        index_map = self._get_index_map(heap)

        if len(index_map) != len(heap_array):
            return False

        for player_id, index in index_map.items():
            if index >= len(heap_array) or index < 0:
                return False
            if heap_array[index].anchor_player.id != player_id:
                return False

        for i, game in enumerate(heap_array):
            if game.anchor_player.id not in index_map:
                return False
            if index_map[game.anchor_player.id] != i:
                return False

        return True

    def _verify_uniqueness_constraint(self, heap: MinHeap) -> bool:
        heap_array = self._get_heap_array(heap)
        player_ids = [game.anchor_player.id for game in heap_array]
        return len(player_ids) == len(set(player_ids))

    def _verify_all_invariants(self, heap: MinHeap) -> None:
        assert self._verify_heap_property(heap), "Min-heap property violated"
        assert self._verify_index_map_consistency(heap), "Index map consistency violated"
        assert self._verify_uniqueness_constraint(heap), "Uniqueness constraint violated"

    def test_when_pushing_multiple_elements_then_invariants_hold(self):
        heap = MinHeap()
        priorities = [10, 5, 15, 3, 7, 12, 20]
        for i, priority in enumerate(priorities):
            heap.push(MockCandidateGame(MockPlayer(i), priority=priority))
            self._verify_all_invariants(heap)

    def test_when_removing_elements_then_invariants_hold(self):
        heap = MinHeap()
        for i in range(7):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(i * 2)))

        for player_id in [3, 5, 1]:
            heap.remove(player_id)
            self._verify_all_invariants(heap)

    def test_when_updating_existing_elements_then_invariants_hold(self):
        heap = MinHeap()
        for i in range(5):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(i)))

        heap.push(MockCandidateGame(MockPlayer(2), priority=100.0))
        self._verify_all_invariants(heap)

        heap.push(MockCandidateGame(MockPlayer(3), priority=0.5))
        self._verify_all_invariants(heap)


class TestConstruction:

    def test_when_creating_empty_heap_then_length_is_zero(self):
        heap = MinHeap()
        assert len(heap) == 0

    def test_when_creating_from_single_element_then_contains_element(self):
        game = MockCandidateGame(MockPlayer(1), priority=5.0)
        heap = MinHeap([game])
        assert len(heap) == 1
        assert 1 in heap

    def test_when_creating_from_multiple_elements_then_contains_all_elements(self):
        games = [MockCandidateGame(MockPlayer(i), priority=float(i)) for i in range(5)]
        heap = MinHeap(games)
        assert len(heap) == 5
        for i in range(5):
            assert i in heap

    def test_when_creating_from_iterable_with_duplicate_players_then_keeps_last(self):
        games = [
            MockCandidateGame(MockPlayer(1), priority=10.0),
            MockCandidateGame(MockPlayer(2), priority=20.0),
            MockCandidateGame(MockPlayer(1), priority=5.0),
        ]
        heap = MinHeap(games)
        assert len(heap) == 2
        assert 1 in heap
        assert 2 in heap

    def test_when_creating_from_iterable_then_min_element_is_accessible(self):
        games = [MockCandidateGame(MockPlayer(i), priority=float(i * 2)) for i in range(5)]
        heap = MinHeap(games)
        assert heap.peek().priority == 0.0


class TestPushMethod:

    def test_when_pushing_to_empty_heap_then_length_increases(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        assert len(heap) == 1
        assert 1 in heap

    def test_when_pushing_game_with_existing_player_then_updates_game(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        assert len(heap) == 1
        assert heap.peek().priority == 5.0

    def test_when_pushing_multiple_games_then_min_is_accessible(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(3), priority=15.0))
        assert heap.peek().priority == 5.0

    def test_when_updating_to_lower_priority_then_becomes_new_min(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(1), priority=1.0))
        assert heap.peek().anchor_player.id == 1
        assert heap.peek().priority == 1.0

    def test_when_updating_to_higher_priority_then_maintains_correct_min(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(1), priority=20.0))
        assert heap.peek().anchor_player.id == 2
        assert heap.peek().priority == 10.0


class TestPeekMethod:

    def test_when_peeking_empty_heap_then_returns_none(self):
        heap = MinHeap()
        assert heap.peek() is None

    def test_when_peeking_single_element_heap_then_returns_that_element(self):
        heap = MinHeap()
        game = MockCandidateGame(MockPlayer(1), priority=5.0)
        heap.push(game)
        assert heap.peek().anchor_player.id == 1
        assert heap.peek().priority == 5.0

    def test_when_peeking_then_does_not_remove_element(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.peek()
        assert len(heap) == 1

    def test_when_peeking_after_operations_then_returns_current_min(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=5.0))
        assert heap.peek().priority == 5.0

        heap.push(MockCandidateGame(MockPlayer(3), priority=3.0))
        assert heap.peek().priority == 3.0


class TestRemoveMethod:

    def test_when_removing_existing_player_then_player_not_in_heap(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.remove(1)
        assert 1 not in heap

    def test_when_removing_existing_player_then_length_decreases(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=10.0))
        heap.remove(1)
        assert len(heap) == 1

    def test_when_removing_nonexistent_player_then_no_error(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.remove(999)
        assert len(heap) == 1

    def test_when_removing_from_empty_heap_then_no_error(self):
        heap = MinHeap()
        heap.remove(1)
        assert len(heap) == 0

    def test_when_removing_all_elements_then_heap_is_empty(self):
        heap = MinHeap()
        player_ids = [1, 2, 3, 4, 5]
        for player_id in player_ids:
            heap.push(MockCandidateGame(MockPlayer(player_id), player_id))

        for player_id in player_ids:
            heap.remove(player_id)

        assert len(heap) == 0

    def test_when_removing_min_element_then_next_min_becomes_top(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(3), priority=15.0))

        heap.remove(1)
        assert heap.peek().priority == 10.0

    def test_when_removing_middle_element_then_heap_remains_valid(self):
        heap = MinHeap()
        for i in range(7):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(i)))

        heap.remove(3)
        assert 3 not in heap
        assert len(heap) == 6
        assert heap.peek().priority == 0.0

    def test_when_removing_last_element_then_heap_remains_valid(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.remove(1)
        assert len(heap) == 0
        assert heap.peek() is None


class TestIndexMethod:

    def test_when_getting_index_of_existing_player_then_returns_valid_index(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        index = heap.index(1)
        assert index >= 0
        assert heap[index].anchor_player.id == 1

    def test_when_getting_index_of_nonexistent_player_then_returns_minus_one(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        assert heap.index(999) == -1

    def test_when_getting_index_from_empty_heap_then_returns_minus_one(self):
        heap = MinHeap()
        assert heap.index(1) == -1

    def test_when_updating_player_then_index_is_updated(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        old_index = heap.index(1)

        heap.push(MockCandidateGame(MockPlayer(1), priority=1.0))
        new_index = heap.index(1)

        assert new_index >= 0
        assert heap[new_index].anchor_player.id == 1


class TestLenMethod:

    def test_when_heap_is_empty_then_length_is_zero(self):
        heap = MinHeap()
        assert len(heap) == 0

    def test_when_heap_has_multiple_elements_then_length_is_correct(self):
        heap = MinHeap()
        for i in range(10):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(i)))
        assert len(heap) == 10

    def test_when_pushing_duplicate_player_then_length_unchanged(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        assert len(heap) == 1

    def test_when_removing_elements_then_length_decreases(self):
        heap = MinHeap()
        for i in range(5):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(i)))

        for i in range(5):
            heap.remove(i)
            assert len(heap) == 4 - i


class TestGetItemMethod:

    def test_when_accessing_valid_index_then_returns_game(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        game = heap[0]
        assert game is not None
        assert game.anchor_player.id == 1

    def test_when_accessing_min_element_then_returns_same_as_peek(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=10.0))
        assert heap[0].anchor_player.id == heap.peek().anchor_player.id

    def test_when_accessing_all_indices_then_all_elements_accessible(self):
        heap = MinHeap()
        player_ids = [1, 2, 3, 4, 5]
        for player_id in player_ids:
            heap.push(MockCandidateGame(MockPlayer(player_id), player_id))

        accessed_ids = set()
        for i in range(len(heap)):
            accessed_ids.add(heap[i].anchor_player.id)

        assert accessed_ids == set(player_ids)

    def test_when_accessing_out_of_bounds_then_raises_index_error(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        with pytest.raises(IndexError):
            _ = heap[10]

    def test_when_accessing_negative_index_then_works_like_list(self):
        heap = MinHeap()
        for i in range(3):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(i)))

        last_element = heap[-1]
        assert last_element is not None


class TestContainsMethod:

    def test_when_player_exists_then_returns_true(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        assert 1 in heap

    def test_when_player_does_not_exist_then_returns_false(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        assert 999 not in heap

    def test_when_checking_empty_heap_then_returns_false(self):
        heap = MinHeap()
        assert 1 not in heap

    def test_when_player_was_removed_then_returns_false(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.remove(1)
        assert 1 not in heap


class TestStrMethod:
    def test_when_converting_empty_heap_to_string_then_returns_empty_list_string(self):
        heap = MinHeap()
        assert str(heap) == "[]"

    def test_when_converting_non_empty_heap_to_string_then_returns_list_representation(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        result = str(heap)
        assert result == "[CandidateGame(anchor=1, imbalance=5.0)]"


class TestEdgeCases:

    def test_when_heap_has_equal_priorities_then_maintains_heap_property(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(3), priority=5.0))

        assert len(heap) == 3
        assert heap.peek().priority == 5.0

    def test_when_using_float_priorities_then_works_correctly(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.5))
        heap.push(MockCandidateGame(MockPlayer(2), priority=5.2))
        heap.push(MockCandidateGame(MockPlayer(3), priority=5.8))

        assert heap.peek().priority == 5.2

    def test_when_large_number_of_elements_then_maintains_correctness(self):
        heap = MinHeap()
        import random

        priorities = [random.random() * 100 for _ in range(1000)]
        for i, priority in enumerate(priorities):
            heap.push(MockCandidateGame(MockPlayer(i), priority=priority))

        assert len(heap) == 1000
        min_priority = min(priorities)
        assert abs(heap.peek().priority - min_priority) < 0.0001

    def test_when_removing_and_re_adding_player_then_works_correctly(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.remove(1)
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))

        assert 1 in heap
        assert heap.index(1) >= 0

    def test_when_alternating_operations_then_maintains_correctness(self):
        heap = MinHeap()

        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=5.0))
        heap.remove(1)
        heap.push(MockCandidateGame(MockPlayer(3), priority=15.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=3.0))

        assert len(heap) == 2
        assert heap.peek().priority == 3.0

    def test_when_updating_min_element_then_heap_reorders_correctly(self):
        heap = MinHeap()
        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(3), priority=15.0))

        heap.push(MockCandidateGame(MockPlayer(1), priority=20.0))

        assert heap.peek().priority == 10.0


class TestComplexScenarios:

    def test_when_simulating_priority_queue_operations_then_maintains_correctness(self):
        heap = MinHeap()

        games = [(1, 5.0), (2, 3.0), (3, 8.0), (4, 1.0), (5, 10.0)]

        for player_id, priority in games:
            heap.push(MockCandidateGame(MockPlayer(player_id), priority=priority))

        assert heap.peek().anchor_player.id == 4

        heap.push(MockCandidateGame(MockPlayer(2), priority=0.5))
        assert heap.peek().anchor_player.id == 2

    def test_when_managing_player_candidates_then_enforces_uniqueness(self):
        heap = MinHeap()

        heap.push(MockCandidateGame(MockPlayer(1), priority=10.0))
        heap.push(MockCandidateGame(MockPlayer(2), priority=20.0))
        heap.push(MockCandidateGame(MockPlayer(3), priority=15.0))

        assert len(heap) == 3

        heap.push(MockCandidateGame(MockPlayer(1), priority=5.0))
        assert len(heap) == 3

        heap.push(MockCandidateGame(MockPlayer(4), priority=12.0))
        assert len(heap) == 4

        player_ids = set()
        for i in range(len(heap)):
            player_ids.add(heap[i].anchor_player.id)
        assert len(player_ids) == 4

    def test_when_processing_heap_sequentially_then_removes_in_priority_order(self):
        heap = MinHeap()
        priorities = [10, 5, 15, 3, 20, 8, 12]

        for i, priority in enumerate(priorities):
            heap.push(MockCandidateGame(MockPlayer(i), priority=float(priority)))

        processed_priorities = []
        while len(heap) > 0:
            min_game = heap.peek()
            processed_priorities.append(min_game.priority)
            heap.remove(min_game.anchor_player.id)

        assert processed_priorities == sorted(priorities)

    def test_when_stress_testing_with_random_operations_then_maintains_consistency(self):
        heap = MinHeap()
        tracking_dict = {}

        random.seed(42)
        for _ in range(200):
            operation = random.choice(['push', 'remove', 'update', 'check'])
            player_id = random.randint(1, 50)
            priority = random.random() * 100

            if operation == 'push':
                heap.push(MockCandidateGame(MockPlayer(player_id), priority=priority))
                tracking_dict[player_id] = priority
            elif operation == 'remove' and player_id in tracking_dict:
                heap.remove(player_id)
                del tracking_dict[player_id]
            elif operation == 'update' and player_id in tracking_dict:
                new_priority = random.random() * 100
                heap.push(MockCandidateGame(MockPlayer(player_id), priority=new_priority))
                tracking_dict[player_id] = new_priority
            elif operation == 'check':
                assert (player_id in heap) == (player_id in tracking_dict)

        assert len(heap) == len(tracking_dict)

        if len(tracking_dict) > 0:
            min_priority = min(tracking_dict.values())
            assert abs(heap.peek().priority - min_priority) == 0.0
