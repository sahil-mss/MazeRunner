"""
Base Search Class and Search Result interface.
All search algorithms inherit from BaseSearch and implement step().
"""
from typing import Optional, List, Tuple
from state import State

class BaseSearch:
    def __init__(self, start_state: State, world):
        self.start_state = start_state
        self.world = world
        self.finished = False
        self.success = False
        self.path: List[Tuple[int, int]] = []
        
        # Performance & Telemetry metrics
        self.expanded_count = 0
        self.generated_count = 0
        self.current_state: Optional[State] = start_state
        self.frontier_states: List[State] = []
        self.explored_states: List[State] = []
        self.parent = {}  # state -> parent_state

    def is_goal(self, state: State) -> bool:
        """Goal condition: all 3 keys collected AND agent at exit position."""
        return len(state.keys) == len(self.world.keys) and state.pos == self.world.exit_pos

    def get_successors(self, state: State) -> List[State]:
        """Generate successor states based on currently passable neighbors."""
        successors = []
        for nr, nc in self.world.get_valid_neighbors(state.r, state.c):
            # Check if this cell contains a key not yet collected
            new_keys = state.keys
            if (nr, nc) in self.world.keys and (nr, nc) not in state.keys:
                new_keys = state.keys | frozenset([(nr, nc)])
            successors.append(State(nr, nc, new_keys))
        return successors

    def reconstruct_path(self, end_state: State) -> List[Tuple[int, int]]:
        """Reconstruct cell coordinate path from start to goal."""
        cell_path = []
        curr = end_state
        while curr is not None:
            cell_path.append(curr.pos)
            curr = self.parent.get(curr)
        cell_path.reverse()
        return cell_path

    def step(self, max_steps: int = 1) -> bool:
        """
        Expands up to max_steps nodes.
        Returns True if search is finished (success or failure), False if still running.
        """
        raise NotImplementedError("Subclasses must implement step()")

    def is_finished(self) -> bool:
        return self.finished

    def get_path(self) -> List[Tuple[int, int]]:
        return self.path
