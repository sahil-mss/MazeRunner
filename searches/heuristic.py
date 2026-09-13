"""
Incremental Heuristic Best-First Search.
Uses an evaluation function emphasizing key attraction and progress.
"""
import heapq
from typing import Set
from state import State
from searches.base_search import BaseSearch
from searches.heuristics import manhattan_dist

class HeuristicSearch(BaseSearch):
    def __init__(self, start_state: State, world):
        super().__init__(start_state, world)
        self.counter = 0
        self.pq = []
        score = self.eval_state(start_state)
        heapq.heappush(self.pq, (score, self.counter, start_state))
        self.visited: Set[State] = set()
        self.parent[start_state] = None
        self.generated_count = 1

    def eval_state(self, state: State) -> float:
        remaining = [k for k in self.world.keys if k not in state.keys]
        if not remaining:
            return manhattan_dist(state.pos, self.world.exit_pos)
        
        # Evaluates key collection order with remaining key penalties
        min_key_dist = min(manhattan_dist(state.pos, k) for k in remaining)
        exit_dist = manhattan_dist(state.pos, self.world.exit_pos)
        return min_key_dist * 2.0 + len(remaining) * 15.0 + exit_dist * 0.3

    def step(self, max_steps: int = 1) -> bool:
        if self.finished:
            return True

        for _ in range(max_steps):
            if not self.pq:
                self.finished = True
                self.success = False
                return True

            score, _, curr = heapq.heappop(self.pq)

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
                    s_val = self.eval_state(succ)
                    heapq.heappush(self.pq, (s_val, self.counter, succ))
                    self.generated_count += 1

        self.frontier_states = [item[2] for item in self.pq[:40]]
        return False
