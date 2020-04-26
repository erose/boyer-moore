from typing import *
import enum
import collections

# This function contains lots of commented-out print statements which are useful for understanding
# the behavior at runtime. Comment them back in to use them. It would be nice to support e.g. a
# DEBUG flag which enables printing, but when we tried this we found it actually meaningfully hurt
# performance.
def horspool_search(needle, haystack):
    needle_index = build_backwards_index(needle)
    # print(needle_index)
    p = 0

    while True:
        # If we've run off the end of the haystack, we know the string is not to be found.
        # print("p+len(needle)", p+len(needle))
        # print("len(haystack)", len(haystack))
        if p+len(needle) > len(haystack):
            return False

        # print(needle, haystack[p:p+len(needle)])
        if needle == haystack[p:p+len(needle)]:
            return True
        else:
            # Look at the last character of the slice of haystack we're focused on, find the index
            # of its last ocurrence in the needle-with-last-character-chopped-off, and jump forward
            # by enough to make sure these are aligned.
            # 
            # TODO: explain why
            #
            # abaaabbababcabdacbaabababc   -->   abaaabbababcabdacbaabababc
            #            -                                     -
            #     abdacabaabd              -->               abdacabaabd
            #            -                                     -
            last_haystack_char = haystack[p+len(needle)-1]
            # print("p", p)
            # print("last_haystack_char", last_haystack_char)
            jump_ahead_by = needle_index.get(last_haystack_char, len(needle))
            jump_ahead_by = max(jump_ahead_by, 1) # Always need to make some progress.

            # print("jump_ahead_by", jump_ahead_by)
            p += jump_ahead_by

        # print()

def build_backwards_index(s) -> Dict[str, int]:
    """
    Returns a dictionary which maps each character in s except the last one to the index of its
    last ocurrence, counting backwards. For example:
    
    build_index("abaca") == { "a": 2, "c": 1, "b": 3 }
    """
    result = {}

    for i, c in enumerate(reversed(s[:-1])):
        if c not in result:
            result[c] = i
    
    return result

# Whole different search algorithms, for comparison.
def naive_search(needle, haystack):
    for i in range(len(haystack)):
        for j in range(len(needle)):
            # If we run out of haystack, we can't match.
            if i + j >= len(haystack):
                return False

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
        self.assertEqual(build_backwards_index("abaca"), { "a": 1, "c": 0, "b": 2 })

class HorspoolTestCase(unittest.TestCase):
    def test_it_works(self):
        self.assertTrue(horspool_search("aba", "baabac"))
        self.assertTrue(horspool_search("cab", "xyzcab"))
        self.assertTrue(horspool_search("cab", ("xyz" * 100) + "cab"))
        self.assertTrue(horspool_search("a", "baabac"))
        self.assertTrue(horspool_search("apple", "xxxxaapple"))
        self.assertTrue(horspool_search("cdc", "bcdcba"))
        self.assertTrue(horspool_search("ccc", "bcccba"))
        self.assertFalse(horspool_search("abx", "baabac"))
        self.assertFalse(horspool_search("abaaaaa", "baabac")) # Needle longer than haystack.

import timeit
def benchmark_with_timeit():
    iterations = int(1e4)
    ways_of_doing_it = [
      ("horspool_search", f'horspool_search(needle, haystack)'),
      ("naive_search", 'naive_search(needle, haystack)'),
      ("branching_search", 'branching_search(needle, haystack)'),
      ("native 'in'", 'needle in haystack'),
    ]
    test_cases = [
        ("same chars from needle organized at random", "cab", "cbabcbabcbabcbcbabcabbcbb"), # I keyboard-mashed to generate this haystack.
        ("needle contains a char not in haystack", "xab", "baccabaccabaccabaccabaccabacca" * 10),
        ("300x other chars (not in needle) and then needle at the end", "cab", ("xyz" * 100) + "cab"),
        ("pretty long needle", "cab" * 5, "baccabaccabaccabaccabaccabacca" * 10),
        ("a lot of far-apart partial matches; interstital non-match", "apple", 10 * (10 * "x" + "app")),
        ("a lot of far-apart partial matches; interstital match", "apple", 10 * (10 * "a" + "app")),
    ]

    for case_name, needle, haystack in test_cases:
        print(case_name)
        for way_name, code in ways_of_doing_it:
            time = timeit.timeit(code, number=iterations, globals={'needle': needle, 'haystack': haystack, **globals()})
            print(f"    {way_name}: {time}")
        print()

import cProfile
def benchmark_with_cprofile():
    cProfile.run(f'horspool_search("cab", ("xyz" * 100) + "cab")')

if __name__ == "__main__":
    benchmark_with_timeit()
    benchmark_with_cprofile()
    unittest.main()
