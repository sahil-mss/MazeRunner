"""
State representations for multi-goal maze search.
"""

class State:
    """
    Search state representing an agent's (row, col) position
    and the set of keys collected so far.
    """
    __slots__ = ('r', 'c', 'keys', '_hash')

    def __init__(self, r: int, c: int, keys: frozenset):
        self.r = r
        self.c = c
        self.keys = keys
        self._hash = hash(((r, c), keys))

    @property
    def pos(self):
        return (self.r, self.c)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.r == other.r and self.c == other.c and self.keys == other.keys

    def __repr__(self):
        return f"State(({self.r}, {self.c}), keys={len(self.keys)})"
