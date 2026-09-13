"""
Incremental Iterative Deepening Search (IDS).
Performs depth-limited DFS with incremental stepping across frames.
"""
from typing import List, Tuple
from state import State
from searches.base_search import BaseSearch

class IDSSearch(BaseSearch):
    def __init__(self, start_state: State, world, max_overall_depth: int = 600):
        super().__init__(start_state, world)
        self.current_limit = 25
        self.max_overall_depth = max_overall_depth
        # Stack stores tuples: (state, current_depth)
        self.stack: List[Tuple[State, int]] = [(start_state, 0)]
        self.visited_depth = {start_state: 0}
        self.parent[start_state] = None
        self.generated_count = 1

    def _reset_iteration(self):
        # Step depth limit forward across iterations
        self.current_limit += 25
        self.stack = [(self.start_state, 0)]
        self.visited_depth = {self.start_state: 0}

    def step(self, max_steps: int = 1) -> bool:
        if self.finished:
            return True

        for _ in range(max_steps):
            if not self.stack:
                if self.current_limit >= self.max_overall_depth:
                    self.finished = True
                    self.success = False
                    return True
                self._reset_iteration()
                continue

            curr, depth = self.stack.pop()
            self.current_state = curr
            self.explored_states.append(curr)
            self.expanded_count += 1

            if self.is_goal(curr):
                self.path = self.reconstruct_path(curr)
                self.finished = True
                self.success = True
                return True

            if depth < self.current_limit:
                successors = self.get_successors(curr)
                for succ in reversed(successors):
                    if succ not in self.visited_depth or self.visited_depth[succ] > depth + 1:
                        self.visited_depth[succ] = depth + 1
                        self.parent[succ] = curr
                        self.stack.append((succ, depth + 1))
                        self.generated_count += 1

        self.frontier_states = [item[0] for item in self.stack[-40:]]
        return False
