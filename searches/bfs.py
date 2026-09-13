"""
Incremental Breadth-First Search (BFS).
Uses collections.deque.
"""
from collections import deque
from typing import Set
from state import State
from searches.base_search import BaseSearch

class BFSSearch(BaseSearch):
    def __init__(self, start_state: State, world):
        super().__init__(start_state, world)
        self.queue = deque([start_state])
        self.visited: Set[State] = {start_state}
        self.parent[start_state] = None
        self.generated_count = 1

    def step(self, max_steps: int = 1) -> bool:
        if self.finished:
            return True

        for _ in range(max_steps):
            if not self.queue:
                self.finished = True
                self.success = False
                return True

            curr = self.queue.popleft()
            self.current_state = curr
            self.explored_states.append(curr)
            self.expanded_count += 1

            if self.is_goal(curr):
                self.path = self.reconstruct_path(curr)
                self.finished = True
                self.success = True
                return True

            for succ in self.get_successors(curr):
                if succ not in self.visited:
                    self.visited.add(succ)
                    self.parent[succ] = curr
                    self.queue.append(succ)
                    self.generated_count += 1

        self.frontier_states = list(self.queue)[:40]
        return False
