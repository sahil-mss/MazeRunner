"""
Incremental Uniform Cost Search (UCS).
Uses a priority queue sorted by path cost g(n).
"""
import heapq
from typing import Dict, Set
from state import State
from searches.base_search import BaseSearch

class UCSSearch(BaseSearch):
    def __init__(self, start_state: State, world):
        super().__init__(start_state, world)
        self.counter = 0
        self.pq = []
        heapq.heappush(self.pq, (0, self.counter, start_state))
        self.cost_so_far: Dict[State, int] = {start_state: 0}
        self.closed: Set[State] = set()
        self.parent[start_state] = None
        self.generated_count = 1

    def step(self, max_steps: int = 1) -> bool:
        if self.finished:
            return True

        for _ in range(max_steps):
            if not self.pq:
                self.finished = True
                self.success = False
                return True

            cost, _, curr = heapq.heappop(self.pq)

            if curr in self.closed:
                continue

            self.closed.add(curr)
            self.current_state = curr
            self.explored_states.append(curr)
            self.expanded_count += 1

            if self.is_goal(curr):
                self.path = self.reconstruct_path(curr)
                self.finished = True
                self.success = True
                return True

            for succ in self.get_successors(curr):
                new_cost = cost + 1  # Standard step cost = 1
                if succ not in self.cost_so_far or new_cost < self.cost_so_far[succ]:
                    self.cost_so_far[succ] = new_cost
                    self.parent[succ] = curr
                    self.counter += 1
                    heapq.heappush(self.pq, (new_cost, self.counter, succ))
                    self.generated_count += 1

        self.frontier_states = [item[2] for item in self.pq[:40]]
        return False
