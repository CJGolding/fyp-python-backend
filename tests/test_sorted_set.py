import random
from typing import Optional

import pytest

from backend.sorted_set import SortedSet, _TreeNode
from tests.mock_classes import MockPlayerComparable


class TestAVLTreeInvariants:

    def _get_root(self, sorted_set: SortedSet) -> Optional[_TreeNode]:
        return sorted_set._SortedSet__root

    def _check_bst_property(self, node: Optional[_TreeNode], min_val=None, max_val=None) -> bool:
        if node is None:
            return True

        if min_val is not None and node.player.value <= min_val:
            return False
        if max_val is not None and node.player.value >= max_val:
            return False

        return (self._check_bst_property(node.left, min_val, node.player.value) and
                self._check_bst_property(node.right, node.player.value, max_val))

    def _check_height_property(self, node: Optional[_TreeNode]) -> tuple[bool, int]:
        if node is None:
            return True, 0

        left_valid, left_height = self._check_height_property(node.left)
        right_valid, right_height = self._check_height_property(node.right)

        actual_height = 1 + max(left_height, right_height)
        height_correct = (node.height == actual_height)

        return left_valid and right_valid and height_correct, actual_height

    def _check_balance_property(self, node: Optional[_TreeNode]) -> bool:
        if node is None:
            return True

        left_height = node.left.height if node.left else 0
        right_height = node.right.height if node.right else 0
        balance_factor = left_height - right_height

        if abs(balance_factor) > 1:
            return False

        return (self._check_balance_property(node.left) and
                self._check_balance_property(node.right))

    def _check_size_property(self, node: Optional[_TreeNode]) -> tuple[bool, int]:
        if node is None:
            return True, 0

        left_valid, left_size = self._check_size_property(node.left)
        right_valid, right_size = self._check_size_property(node.right)

        actual_size = 1 + left_size + right_size
        size_correct = (node.size == actual_size)

        return left_valid and right_valid and size_correct, actual_size

    def _verify_all_invariants(self, sorted_set: SortedSet) -> None:
        root = self._get_root(sorted_set)

        assert self._check_bst_property(root), "BST property violated"

        height_valid, _ = self._check_height_property(root)
        assert height_valid, "Height property violated"
        assert self._check_balance_property(root), "AVL balance property violated"

        size_valid, _ = self._check_size_property(root)
        assert size_valid, "Size property violated"

    def test_when_creating_empty_tree_then_invariants_hold(self):
        sorted_set = SortedSet()
        self._verify_all_invariants(sorted_set)

    def test_when_adding_multiple_elements_then_invariants_hold(self):
        sorted_set = SortedSet()
        for val in [10, 5, 15, 3, 7, 12, 20]:
            sorted_set.add(MockPlayerComparable(val))
            self._verify_all_invariants(sorted_set)

    def test_when_adding_sequential_elements_then_invariants_hold(self):
        sorted_set = SortedSet()
        for val in range(1, 11):
            sorted_set.add(MockPlayerComparable(val))
            self._verify_all_invariants(sorted_set)

    def test_when_removing_elements_then_invariants_hold(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [10, 5, 15, 3, 7, 12, 20]])
        for val in [3, 15, 10]:
            sorted_set.remove(MockPlayerComparable(val))
            self._verify_all_invariants(sorted_set)


class TestConstruction:

    def test_when_creating_empty_set_then_length_is_zero(self):
        sorted_set = SortedSet()
        assert len(sorted_set) == 0

    def test_when_creating_from_multiple_elements_then_contains_all_elements(self):
        values = [5, 3, 8, 1, 9]
        sorted_set = SortedSet([MockPlayerComparable(v) for v in values])
        assert len(sorted_set) == 5
        for v in values:
            assert MockPlayerComparable(v) in sorted_set

    def test_when_creating_from_iterable_with_duplicates_then_stores_unique_elements(self):
        sorted_set = SortedSet(
            [MockPlayerComparable(5), MockPlayerComparable(3), MockPlayerComparable(5), MockPlayerComparable(8),
             MockPlayerComparable(3)])
        assert len(sorted_set) == 3
        assert MockPlayerComparable(5) in sorted_set
        assert MockPlayerComparable(3) in sorted_set
        assert MockPlayerComparable(8) in sorted_set

    def test_when_creating_from_unsorted_iterable_then_elements_are_sorted(self):
        values = [5, 2, 8, 1, 9, 3]
        sorted_set = SortedSet([MockPlayerComparable(v) for v in values])
        result = [p.value for p in sorted_set]
        assert result == sorted(values)


class TestAddMethod:

    def test_when_adding_to_empty_set_then_length_increases(self):
        sorted_set = SortedSet()
        sorted_set.add(MockPlayerComparable(5))
        assert len(sorted_set) == 1
        assert MockPlayerComparable(5) in sorted_set

    def test_when_adding_duplicate_element_then_length_unchanged(self):
        sorted_set = SortedSet([MockPlayerComparable(5)])
        sorted_set.add(MockPlayerComparable(5))
        assert len(sorted_set) == 1

    def test_when_adding_multiple_elements_then_maintains_sorted_order(self):
        sorted_set = SortedSet()
        values = [5, 2, 8, 1, 9]
        for v in values:
            sorted_set.add(MockPlayerComparable(v))
        result = [p.value for p in sorted_set]
        assert result == sorted(values)


class TestRemoveMethod:

    def test_when_removing_existing_element_then_element_not_in_set(self):
        sorted_set = SortedSet([MockPlayerComparable(5), MockPlayerComparable(3), MockPlayerComparable(8)])
        sorted_set.remove(MockPlayerComparable(5))
        assert MockPlayerComparable(5) not in sorted_set
        assert len(sorted_set) == 2

    def test_when_removing_nonexistent_element_then_raises_value_error(self):
        sorted_set = SortedSet([MockPlayerComparable(5)])
        with pytest.raises(ValueError, match="Player\\(10\\) is not in SortedSet"):
            sorted_set.remove(MockPlayerComparable(10))

    def test_when_removing_from_empty_set_then_raises_value_error(self):
        sorted_set = SortedSet()
        with pytest.raises(ValueError):
            sorted_set.remove(MockPlayerComparable(5))

    def test_when_removing_elements_then_maintains_sorted_order(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9, 3]])
        sorted_set.remove(MockPlayerComparable(5))
        sorted_set.remove(MockPlayerComparable(1))
        result = [p.value for p in sorted_set]
        assert result == [2, 3, 8, 9]

    def test_when_removing_root_with_two_children_then_tree_remains_valid(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 3, 8, 1, 4, 7, 9]])
        sorted_set.remove(MockPlayerComparable(5))
        assert MockPlayerComparable(5) not in sorted_set
        assert len(sorted_set) == 6
        result = [p.value for p in sorted_set]
        assert result == [1, 3, 4, 7, 8, 9]


class TestLenMethod:

    def test_when_set_is_empty_then_length_is_zero(self):
        sorted_set = SortedSet()
        assert len(sorted_set) == 0

    def test_when_set_has_multiple_elements_then_length_is_correct(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in range(10)])
        assert len(sorted_set) == 10

    def test_when_adding_elements_then_length_increases(self):
        sorted_set = SortedSet()
        for i in range(5):
            sorted_set.add(MockPlayerComparable(i))
            assert len(sorted_set) == i + 1


class TestGetItemMethod:

    def test_when_accessing_elements_by_index_then_returns_correct_value(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9]])
        assert sorted_set[0].value == 1
        assert sorted_set[2].value == 5
        assert sorted_set[4].value == 9

    def test_when_accessing_with_negative_index_then_counts_from_end(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9]])
        assert sorted_set[-1].value == 9
        assert sorted_set[-2].value == 8

    def test_when_accessing_all_indices_then_returns_sorted_order(self):
        values = [5, 2, 8, 1, 9, 3]
        sorted_set = SortedSet([MockPlayerComparable(v) for v in values])
        result = [sorted_set[i].value for i in range(len(sorted_set))]
        assert result == sorted(values)

    def test_when_accessing_out_of_bounds_index_then_raises_index_error(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        with pytest.raises(IndexError, match="SortedSet index out of range"):
            _ = sorted_set[5]
        with pytest.raises(IndexError, match="SortedSet index out of range"):
            _ = sorted_set[-10]

    def test_when_accessing_empty_set_then_raises_index_error(self):
        sorted_set = SortedSet()
        with pytest.raises(IndexError):
            _ = sorted_set[0]

    def test_when_accessing_with_invalid_type_then_raises_type_error(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        with pytest.raises(TypeError, match="Indices must be integers or slices"):
            _ = sorted_set["invalid"]


class TestGetItemSlice:

    def test_when_slicing_set_then_returns_correct_elements(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9]])
        assert [p.value for p in sorted_set[:]] == [1, 2, 5, 8, 9]
        assert [p.value for p in sorted_set[:3]] == [1, 2, 5]
        assert [p.value for p in sorted_set[3:]] == [8, 9]
        assert [p.value for p in sorted_set[1:4]] == [2, 5, 8]

    def test_when_slicing_with_step_then_returns_correct_elements(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in range(10)])
        result = [p.value for p in sorted_set[::2]]
        assert result == [0, 2, 4, 6, 8]

    def test_when_slicing_with_negative_indices_then_returns_correct_slice(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9]])
        result = [p.value for p in sorted_set[-3:-1]]
        assert result == [5, 8]

    def test_when_slicing_empty_range_then_returns_empty_list(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        result = sorted_set[2:2]
        assert result == []

    def test_when_slicing_with_reverse_step_then_returns_reversed_elements(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9]])
        result = [p.value for p in sorted_set[::-1]]
        assert result == [9, 8, 5, 2, 1]


class TestIterMethod:

    def test_when_iterating_empty_set_then_yields_nothing(self):
        sorted_set = SortedSet()
        result = list(sorted_set)
        assert result == []

    def test_when_iterating_set_then_yields_elements_in_sorted_order(self):
        values = [5, 2, 8, 1, 9, 3]
        sorted_set = SortedSet([MockPlayerComparable(v) for v in values])
        result = [p.value for p in sorted_set]
        assert result == sorted(values)

    def test_when_iterating_set_with_duplicates_added_then_yields_unique_sorted_elements(self):
        sorted_set = SortedSet()
        for v in [5, 3, 5, 1, 3]:
            sorted_set.add(MockPlayerComparable(v))
        result = [p.value for p in sorted_set]
        assert result == [1, 3, 5]


class TestContainsMethod:

    def test_when_element_exists_then_returns_true(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3, 4, 5]])
        assert MockPlayerComparable(3) in sorted_set

    def test_when_element_does_not_exist_then_returns_false(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3, 4, 5]])
        assert MockPlayerComparable(10) not in sorted_set

    def test_when_checking_empty_set_then_returns_false(self):
        sorted_set = SortedSet()
        assert MockPlayerComparable(1) not in sorted_set

    def test_when_element_was_removed_then_returns_false(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        sorted_set.remove(MockPlayerComparable(2))
        assert MockPlayerComparable(2) not in sorted_set


class TestIndexMethod:

    def test_when_finding_index_of_elements_then_returns_correct_index(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8, 1, 9]])
        assert sorted_set.index(MockPlayerComparable(1)) == 0
        assert sorted_set.index(MockPlayerComparable(5)) == 2
        assert sorted_set.index(MockPlayerComparable(9)) == 4

    def test_when_finding_index_of_all_elements_then_indices_are_correct(self):
        values = [5, 2, 8, 1, 9]
        sorted_set = SortedSet([MockPlayerComparable(v) for v in values])
        sorted_values = sorted(values)
        for i, v in enumerate(sorted_values):
            assert sorted_set.index(MockPlayerComparable(v)) == i

    def test_when_finding_index_of_nonexistent_element_then_raises_value_error(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        with pytest.raises(ValueError, match="Player\\(10\\) is not in SortedSet"):
            sorted_set.index(MockPlayerComparable(10))

    def test_when_finding_index_in_empty_set_then_raises_value_error(self):
        sorted_set = SortedSet()
        with pytest.raises(ValueError):
            sorted_set.index(MockPlayerComparable(1))


class TestReprMethod:

    def test_when_set_is_empty_then_repr_shows_empty_list(self):
        sorted_set = SortedSet()
        assert repr(sorted_set) == "SortedSet([])"

    def test_when_set_has_elements_then_repr_shows_sorted_list(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [5, 2, 8]])
        result = repr(sorted_set)
        assert result == "SortedSet([Player(2), Player(5), Player(8)])"


class TestEdgeCases:

    def test_when_adding_large_number_of_elements_then_maintains_correctness(self):
        sorted_set = SortedSet()
        values = list(range(1000))
        random.shuffle(values)

        for v in values:
            sorted_set.add(MockPlayerComparable(v))

        assert len(sorted_set) == 1000
        result = [p.value for p in sorted_set]
        assert result == list(range(1000))

    def test_when_accessing_indices_after_modifications_then_indices_are_correct(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3, 4, 5]])
        sorted_set.remove(MockPlayerComparable(3))
        sorted_set.add(MockPlayerComparable(6))

        assert sorted_set[0].value == 1
        assert sorted_set[2].value == 4
        assert sorted_set[-1].value == 6

    def test_when_alternating_add_and_remove_then_maintains_correctness(self):
        sorted_set = SortedSet()

        sorted_set.add(MockPlayerComparable(5))
        sorted_set.add(MockPlayerComparable(3))
        sorted_set.remove(MockPlayerComparable(5))
        sorted_set.add(MockPlayerComparable(7))
        sorted_set.add(MockPlayerComparable(1))
        sorted_set.remove(MockPlayerComparable(3))

        result = [p.value for p in sorted_set]
        assert result == [1, 7]

    def test_when_using_same_value_multiple_times_then_set_contains_one_instance(self):
        sorted_set = SortedSet()
        for _ in range(10):
            sorted_set.add(MockPlayerComparable(5))
        assert len(sorted_set) == 1
        assert MockPlayerComparable(5) in sorted_set

    def test_when_removing_and_re_adding_element_then_element_exists(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        sorted_set.remove(MockPlayerComparable(2))
        sorted_set.add(MockPlayerComparable(2))
        assert MockPlayerComparable(2) in sorted_set
        assert sorted_set.index(MockPlayerComparable(2)) == 1

    def test_when_creating_from_generator_then_works_correctly(self):
        sorted_set = SortedSet(MockPlayerComparable(i) for i in range(5))
        result = [p.value for p in sorted_set]
        assert result == [0, 1, 2, 3, 4]

    def test_when_slicing_beyond_bounds_then_returns_available_elements(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in [1, 2, 3]])
        result = [p.value for p in sorted_set[:10]]
        assert result == [1, 2, 3]

    def test_when_using_negative_step_slice_with_bounds_then_returns_correct_elements(self):
        sorted_set = SortedSet([MockPlayerComparable(i) for i in range(10)])
        result = [p.value for p in sorted_set[8:2:-2]]
        assert result == [8, 6, 4]


class TestComplexScenarios:

    def test_when_building_set_incrementally_then_maintains_sorted_order_throughout(self):
        sorted_set = SortedSet()
        values_to_add = [50, 25, 75, 10, 30, 60, 80, 5, 15, 27, 35]

        for i, v in enumerate(values_to_add):
            sorted_set.add(MockPlayerComparable(v))
            result = [p.value for p in sorted_set]
            assert result == sorted(values_to_add[:i + 1])

    def test_when_bulk_operations_then_maintains_consistency(self):
        values = [i for i in range(1, 21)]
        sorted_set = SortedSet([MockPlayerComparable(v) for v in values])

        for v in range(2, 21, 2):
            sorted_set.remove(MockPlayerComparable(v))

        result = [p.value for p in sorted_set]
        assert result == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

        for v in [2, 6, 10]:
            sorted_set.add(MockPlayerComparable(v))

        result = [p.value for p in sorted_set]
        assert result == [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 15, 17, 19]

    def test_when_stress_testing_with_random_operations_then_maintains_consistency(self):
        sorted_set = SortedSet()
        tracking_set = set()

        random.seed(42)
        for _ in range(100):
            operation = random.choice(['add', 'remove', 'contains'])
            value = random.randint(1, 50)

            if operation == 'add':
                sorted_set.add(MockPlayerComparable(value))
                tracking_set.add(value)
            elif operation == 'remove' and value in tracking_set:
                sorted_set.remove(MockPlayerComparable(value))
                tracking_set.remove(value)
            elif operation == 'contains':
                assert (MockPlayerComparable(value) in sorted_set) == (value in tracking_set)

        assert len(sorted_set) == len(tracking_set)
        result = [p.value for p in sorted_set]
        assert result == sorted(tracking_set)
