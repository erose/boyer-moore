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

    result = {}
    for i, c in enumerate(reversed(s)):
        if c in result:
            continue
        result[c] = i

    return result

def build_forwards_index(s) -> Dict[str, int]:
    """
    Returns a dictionary which maps each character in s to its index, starting from the front of the
    string. (e.g. the first character is at index 0).
    """

    result = {}
    for i, c in enumerate(s):
        if c in result:
            continue
        result[c] = i

    return result

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

# Whole different search algorithms, for comparison.
def naive_search(needle, haystack):
    for i in range(len(haystack)):
        for j in range(len(needle)):
            if haystack[i + j] != needle[j]:
                break
        else:
            return True

    return False

def branching_search(needle, haystack):
    # For each character in haystack, what positions does it occur at?
    positions = collections.defaultdict(set)
    for i, c in enumerate(haystack):
        positions[c].add(i)

    # Winnow down the possible positions; for each character, check its positions and see if they
    # are possible given the positions of the previous characters.
    possible = positions[needle[0]]
    for c in needle[1:]:
        possible = { p for p in positions[c] if p - 1 in possible }
    
    return len(possible) != 0

import unittest
class NaiveSearchTestCase(unittest.TestCase):
    def test_it_works(self):
        self.assertTrue(naive_search("aba", "baabac"))
        self.assertTrue(naive_search("cab", "xyzcab"))
        self.assertTrue(naive_search("cab", ("xyz" * 100) + "cab"))
        self.assertTrue(naive_search("a", "baabac"))

        self.assertFalse(naive_search("abx", "baabac"))
        self.assertFalse(naive_search("abaaaaa", "baabac")) # Needle longer than haystack.

class BranchingSearchTestCase(unittest.TestCase):
    def test_it_works(self):
        self.assertTrue(branching_search("aba", "baabac"))
        self.assertTrue(branching_search("cab", "xyzcab"))
        self.assertTrue(branching_search("cab", ("xyz" * 100) + "cab"))
        self.assertTrue(branching_search("a", "baabac"))

        self.assertFalse(branching_search("abx", "baabac"))
        self.assertFalse(branching_search("abaaaaa", "baabac")) # Needle longer than haystack.

class TestBuildIndexes(unittest.TestCase):
    def test_build_backwards_index(self):
        self.assertEqual(build_backwards_index("asab"), {'b': 0, 'a': 1, 's': 2})

    def test_build_forwards_index(self):
        self.assertEqual(build_forwards_index("asab"), {'a': 0, 's': 1, 'b': 3})

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
    ways_of_doing_it = [
        *[
            (direction.value, f'search(needle, haystack, {direction})') for direction in Direction
        ],
        ("naive_search", 'naive_search(needle, haystack)'),
        ("branching_search", 'branching_search(needle, haystack)'),
        ("native 'in'", 'needle in haystack'),
    ]
    test_cases = [
        ("same chars from needle organized at random", "cab", "cbabcbabcbabcbcbabcabbcbb"), # I keyboard-mashed to generate this haystack.
        ("needle contains a char not in haystack", "xab", "baccabaccabaccabaccabaccabacca"),
        ("300x other chars (not in needle) and then needle at the end", "cab", ("xyz" * 100) + "cab"),
    ]

    for case_name, needle, haystack in test_cases:
        print(case_name)
        for way_name, code in ways_of_doing_it:
            time = timeit.timeit(code, number=iterations, globals={'needle': needle, 'haystack': haystack, **globals()})
            print(f"    {way_name}: {time}")
        print()

import cProfile
def benchmark_with_cprofile():
    for direction in ['Direction.backwards', 'Direction.forwards', 'Direction.forwards_with_needle_index']:
        print(f'{direction}')
        cProfile.run(f'search("cab", ("xyz" * 100) + "cab", {direction})')

if __name__ == "__main__":
    benchmark_with_timeit()
    benchmark_with_cprofile()
    unittest.main()
