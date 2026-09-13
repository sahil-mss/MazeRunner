"""
Incremental Depth-First Search (DFS).
Uses a LIFO stack.
"""
from typing import List, Set
from state import State
from searches.base_search import BaseSearch

class DFSSearch(BaseSearch):
    def __init__(self, start_state: State, world):
        super().__init__(start_state, world)
        self.stack: List[State] = [start_state]
        self.visited: Set[State] = {start_state}
        self.parent[start_state] = None
        self.generated_count = 1

    def step(self, max_steps: int = 1) -> bool:
        if self.finished:
            return True

        for _ in range(max_steps):
            if not self.stack:
                self.finished = True
                self.success = False
                return True

            curr = self.stack.pop()
            self.current_state = curr
            self.explored_states.append(curr)
            self.expanded_count += 1

            if self.is_goal(curr):
                self.path = self.reconstruct_path(curr)
                self.finished = True
                self.success = True
                return True

            successors = self.get_successors(curr)
            # Reverse order so first neighbor is popped first
            for succ in reversed(successors):
                if succ not in self.visited:
                    self.visited.add(succ)
                    self.parent[succ] = curr
                    self.stack.append(succ)
                    self.generated_count += 1

        self.frontier_states = list(self.stack[-40:])
        return False
