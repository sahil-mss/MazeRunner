"""
Incremental Greedy Best-First Search.
Priority determined solely by heuristic value h(n).
"""
import heapq
from typing import Set
from state import State
from searches.base_search import BaseSearch
from searches.heuristics import calculate_heuristic

class GreedySearch(BaseSearch):
    def __init__(self, start_state: State, world):
        super().__init__(start_state, world)
        self.counter = 0
        self.pq = []
        h_val = calculate_heuristic(start_state, world)
        heapq.heappush(self.pq, (h_val, self.counter, start_state))
        self.visited: Set[State] = set()
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

            h_val, _, curr = heapq.heappop(self.pq)

            if curr in self.visited:
                continue

            self.visited.add(curr)
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
                    self.parent[succ] = curr
                    self.counter += 1
                    succ_h = calculate_heuristic(succ, self.world)
                    heapq.heappush(self.pq, (succ_h, self.counter, succ))
                    self.generated_count += 1

        self.frontier_states = [item[2] for item in self.pq[:40]]
        return False
