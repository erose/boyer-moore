from typing import *
import enum
import collections

class Direction(enum.Enum):
    forwards = 'forwards'
    backwards = 'backwards'

def search(needle, haystack, direction=Direction.forwards):
    if direction == Direction.backwards:
        needle_backwards_index = build_backwards_index(needle)
    if direction == Direction.forwards:
        haystack_forwards_index = build_forwards_index(haystack)

    haystack_position = len(needle) - 1
    while True:
        if haystack_position >= len(haystack):
            return False

        if direction == Direction.backwards:
            result, jump_ahead_by = compare_from_back(needle, haystack, haystack_position, needle_backwards_index)
        if direction == Direction.forwards:
            result, jump_ahead_by = compare_from_front(needle, haystack, haystack_position, haystack_forwards_index)
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
            jump_ahead_by = needle_backwards_index.get(needle_char, len(needle))

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
            return False, jump_ahead_by

    return True, None

import unittest
class TestForwardsBoyerMoore(unittest.TestCase):
    def test_it_works(self):
        self.assertTrue(search("aba", "baabac", Direction.forwards))
        self.assertTrue(search("a", "baabac", Direction.forwards))
        self.assertFalse(search("abx", "baabac", Direction.forwards))
        self.assertFalse(search("abaaaaa", "baabac", Direction.forwards)) # Needle longer than haystack.

class TestBackwardsBoyerMoore(unittest.TestCase):
    def test_it_works(self):
        self.assertTrue(search("aba", "baabac", Direction.backwards))
        self.assertTrue(search("a", "baabac", Direction.backwards))
        self.assertFalse(search("abx", "baabac", Direction.backwards))
        self.assertFalse(search("abaaaaa", "baabac", Direction.backwards)) # Needle longer than haystack.

if __name__ == "__main__":
    unittest.main()
