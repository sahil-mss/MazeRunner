"""
Incremental A* Search.
f(n) = g(n) + h(n)
"""
import heapq
from typing import Dict, Set
from state import State
from searches.base_search import BaseSearch
from searches.heuristics import calculate_heuristic

class AStarSearch(BaseSearch):
    def __init__(self, start_state: State, world):
        super().__init__(start_state, world)
        self.counter = 0
        self.pq = []
        self.g_score: Dict[State, int] = {start_state: 0}
        h_val = calculate_heuristic(start_state, world)
        heapq.heappush(self.pq, (h_val, self.counter, start_state))
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

            f_score, _, curr = heapq.heappop(self.pq)

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

            current_g = self.g_score[curr]

            for succ in self.get_successors(curr):
                tentative_g = current_g + 1
                if succ in self.closed:
                    continue

                if succ not in self.g_score or tentative_g < self.g_score[succ]:
                    self.g_score[succ] = tentative_g
                    self.parent[succ] = curr
                    self.counter += 1
                    h_val = calculate_heuristic(succ, self.world)
                    f_val = tentative_g + h_val
                    heapq.heappush(self.pq, (f_val, self.counter, succ))
                    self.generated_count += 1

        self.frontier_states = [item[2] for item in self.pq[:40]]
        return False
