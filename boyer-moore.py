from typing import *
import enum
import collections

class Direction(enum.Enum):
    forwards = 'forwards'
    forwards_with_needle_index = 'forwards_with_needle_index'
    backwards = 'backwards'

def search(needle, haystack, direction):
    if direction == Direction.backwards:
        needle_backwards_index = build_backwards_index(needle)
        haystack_position = len(needle) - 1
    if direction == Direction.forwards:
        haystack_forwards_index = build_forwards_index(haystack)
        haystack_position = 0
    if direction == Direction.forwards_with_needle_index:
        needle_forwards_index = build_forwards_index(needle)
        haystack_position = 0

    while True:
        # If we've run off the end of the haystack, we know the string is not to be found.
        if haystack_position >= len(haystack):
            return False

        if direction == Direction.backwards:
            result, jump_ahead_by = compare_from_back(needle, haystack, haystack_position, needle_backwards_index)
        if direction == Direction.forwards:
            result, jump_ahead_by = compare_from_front(needle, haystack, haystack_position, haystack_forwards_index)
        if direction == Direction.forwards_with_needle_index:
            result, jump_ahead_by = compare_from_front(needle, haystack, haystack_position, needle_forwards_index)
        if result is True:
            return True
        else:
            haystack_position += jump_ahead_by

def build_backwards_index(s) -> Dict[str, int]:
    """
    Returns a dictionary which maps each character in s to its index, starting from the back of the
    string. (e.g. the final character is at index 0).
    """
    unique_characters = set(s)
    return { c: len(s) - (s.rindex(c) + 1) for c in unique_characters }

def build_forwards_index(s) -> Dict[str, int]:
    unique_characters = set(s)
    return { c: s.index(c) for c in unique_characters }

def compare_from_back(needle, haystack, haystack_position, needle_backwards_index) -> Tuple[int, bool]:
    for k in range(0, len(needle)):
        needle_char = needle[-(k + 1)]
        haystack_char = haystack[haystack_position - k]

        if needle_char != haystack_char:
            # Snap to the next ocurrence of this character.
            # e.g.
            #
            # aba     -->   aba
            # -             -
            #
            # cbacba  --> cbacba
            # -             -
            #
            jump_ahead_by = needle_backwards_index.get(haystack_char, len(needle))

            # Dan's claim: if we do more work on the index building, we can be smarter here.
            jump_ahead_by = max(1, jump_ahead_by)
            return False, jump_ahead_by

    return True, None

def compare_from_front(needle, haystack, haystack_position, haystack_forwards_index) -> Tuple[int, bool]:
    for k in range(0, len(needle)):
        needle_char = needle[k]
        haystack_char = haystack[haystack_position + k]

        if needle_char != haystack_char:
            # Snap to the next ocurrence of this character.
            # e.g.
            #
            # aba     -->   aba
            # -             -
            #
            # cbacba  --> cbacba
            # -             -
            #
            jump_ahead_by = haystack_forwards_index.get(needle_char, len(haystack))

            # Dan's claim: if we do more work on the index building, we can be smarter here.
            jump_ahead_by = max(1, jump_ahead_by)
            return False, jump_ahead_by

    return True, None

import unittest
class BoyerMooreTestCase(unittest.TestCase):
    def do_test_for_direction(self, direction):
        self.assertTrue(search("aba", "baabac", direction))
        self.assertTrue(search("cab", "xyzcab", direction))
        self.assertTrue(search("cab", ("xyz" * 100) + "cab", direction))
        self.assertTrue(search("a", "baabac", direction))

        self.assertFalse(search("abx", "baabac", direction))
        self.assertFalse(search("abaaaaa", "baabac", direction)) # Needle longer than haystack.

class TestForwardsBoyerMoore(BoyerMooreTestCase):
    def test_it_works(self):
        self.do_test_for_direction(Direction.forwards)

class TestForwardsWithNeedleIndexBoyerMoore(BoyerMooreTestCase):
    def test_it_works(self):
        self.do_test_for_direction(Direction.forwards_with_needle_index)

class TestBackwardsBoyerMoore(BoyerMooreTestCase):
    def test_it_works(self):
        self.do_test_for_direction(Direction.backwards)

import timeit
def benchmark_with_timeit():
    iterations = int(1e4)
    for direction in Direction:
        time = timeit.timeit(lambda: search("cab", ("xyz" * 100) + "cab", direction), number=iterations)
        print(f"{direction.value}: {time}")

import cProfile
def benchmark_with_cprofile():
    for direction in ['Direction.backwards', 'Direction.forwards', 'Direction.forwards_with_needle_index']:
        cProfile.run(f'search("cab", ("xyz" * 10000) + "cab", {direction})')

if __name__ == "__main__":
    benchmark_with_timeit()
    benchmark_with_cprofile()
    unittest.main()
