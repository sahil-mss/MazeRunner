"""
Agent class.
Encapsulates an AI agent, its search algorithm, physical position, collected keys,
performance telemetry, and responsive movement timers.
"""
from typing import List, Tuple, Optional
from collections import deque
from state import State
from config import MAX_SEARCH_STEPS_PER_FRAME

class Agent:
    def __init__(self, name: str, color: Tuple[int, int, int], search_cls, world):
        self.name = name
        self.color = color
        self.search_cls = search_cls
        self.world = world

        # Position and state
        self.r, self.c = world.start_pos
        self.collected_keys = frozenset()
        self.finished = False
        self.finish_time: Optional[float] = None
        self.status = "SEARCHING"  # "SEARCHING", "MOVING", "REPLANNING", "OPENING_DOOR", "FINISHED"

        # Movement path and execution
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.move_accumulator = 0.0
        self.steps_taken = 0

        # Telemetry & Metrics
        self.search_instance = None
        self.last_world_revision = -1
        self.replans_count = 0
        self.total_expanded = 0
        self.total_generated = 0
        self.max_frontier_size = 0
        self.last_frontier_size = 0
        self.final_path_length = 0

        self.start_new_search()

    @property
    def pos(self):
        return (self.r, self.c)

    def current_state(self) -> State:
        return State(self.r, self.c, self.collected_keys)

    def start_new_search(self):
        """Initiates an incremental search starting from agent's current position and keys."""
        state = self.current_state()
        self.search_instance = self.search_cls(state, self.world)
        self.path = []
        self.path_index = 0
        self.last_world_revision = self.world.revision
        self.status = "SEARCHING"

    def _bfs_passable_path(self, start_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Calculates a strictly passable path between start and target avoiding closed doors."""
        if start_pos == target_pos:
            return [start_pos]
        queue = deque([start_pos])
        parent = {start_pos: None}
        while queue:
            curr = queue.popleft()
            if curr == target_pos:
                path = []
                c = curr
                while c is not None:
                    path.append(c)
                    c = parent[c]
                path.reverse()
                return path
            for nr, nc in self.world.get_valid_neighbors(curr[0], curr[1], allow_hypothetical=False):
                if (nr, nc) not in parent:
                    parent[(nr, nc)] = curr
                    queue.append((nr, nc))
        return []

    def handle_blocked_path(self, blocked_pos: Optional[Tuple[int, int]] = None):
        """
        When stuck or blocked by a closed door:
        Priority 1: Recalculate another passable path to the uncollected key(s) or exit.
        Priority 2: If fail (blocked in front), calculate path to the open partner door of that color
                    to pass through it and flip the closed door open!
        """
        self.replans_count += 1
        self.status = "REPLANNING"

        # 1. First Priority: Try to find a direct passable route to remaining goals
        # Check remaining keys or exit
        remaining_keys = [k for k in self.world.keys if k not in self.collected_keys]
        targets = remaining_keys if remaining_keys else [self.world.exit_pos]

        best_direct_path = None
        for t in targets:
            p = self._bfs_passable_path(self.pos, t)
            if p and len(p) > 1:
                if best_direct_path is None or len(p) < len(best_direct_path):
                    best_direct_path = p

        if best_direct_path:
            self.path = best_direct_path
            self.path_index = 0
            self.status = "MOVING"
            return

        # 2. Second Priority: Open the closed door in front of us!
        # Find the closed door blocking us
        closed_door = self.world.door_map.get(blocked_pos) if blocked_pos else None
        if not closed_door:
            # Check adjacent closed doors
            for nr, nc in self.world.maze.get_neighbors(self.r, self.c):
                d = self.world.door_map.get((nr, nc))
                if d and not self.world.is_door_open(d):
                    closed_door = d
                    break

        if closed_door:
            # Partner door of this color is currently open (1)!
            partner_door = self.world.get_partner_door(closed_door)
            if partner_door and self.world.is_door_open(partner_door):
                partner_path = self._bfs_passable_path(self.pos, partner_door.pos)
                if partner_path and len(partner_path) > 1:
                    self.path = partner_path
                    self.path_index = 0
                    self.status = "OPENING_DOOR"
                    return

        # Fallback: run standard search from current state
        self.start_new_search()

    def update(self, dt: float, move_speed: float, current_time: float) -> bool:
        """
        Updates search and movement incrementally.
        dt: delta time in seconds.
        move_speed: cells per second.
        current_time: total elapsed race time.
        Returns True if this agent reached the winning condition on this update.
        """
        if self.finished:
            self.status = "FINISHED"
            return False

        # 1. Environment Change Detection & Adversarial Blocking Check
        if self.world.revision != self.last_world_revision:
            self.last_world_revision = self.world.revision
            if self.path and not self._is_path_passable():
                first_blocked = None
                for pr, pc in self.path[self.path_index:]:
                    if not self.world.is_cell_passable(pr, pc):
                        first_blocked = (pr, pc)
                        break
                self.handle_blocked_path(first_blocked)

        # 2. Search Execution (if path not yet found):
        if not self.path:
            if self.search_instance is not None and not self.search_instance.is_finished():
                if self.status not in ("REPLANNING", "OPENING_DOOR"):
                    self.status = "SEARCHING"
                # Expand a bounded number of nodes per frame to NEVER freeze the UI
                self.search_instance.step(MAX_SEARCH_STEPS_PER_FRAME)
                
                # Update live telemetry stats
                self.total_expanded = self.search_instance.expanded_count
                self.total_generated = self.search_instance.generated_count
                self.last_frontier_size = len(self.search_instance.frontier_states)
                if self.last_frontier_size > self.max_frontier_size:
                    self.max_frontier_size = self.last_frontier_size

                if self.search_instance.is_finished():
                    if self.search_instance.success:
                        self.path = self.search_instance.get_path()
                        self.path_index = 0
                        self.final_path_length = len(self.path)
                        self.status = "MOVING"
                    else:
                        # Search failed (completely blocked) -> trigger second priority to open door
                        self.handle_blocked_path()

        # 3. Responsive Movement (moving cell by cell):
        if self.path and self.path_index < len(self.path):
            if self.status != "OPENING_DOOR":
                self.status = "MOVING"
            self.move_accumulator += dt
            step_interval = 1.0 / move_speed

            while self.move_accumulator >= step_interval:
                self.move_accumulator -= step_interval
                
                # Next step coordinate
                next_pos = self.path[self.path_index]
                
                # If path starts at current position, advance to next
                if next_pos == self.pos:
                    self.path_index += 1
                    if self.path_index >= len(self.path):
                        self.path = []
                        break
                    next_pos = self.path[self.path_index]

                # Check if next step is blocked by a closed door (door state = 0)
                if not self.world.is_cell_passable(next_pos[0], next_pos[1]):
                    # Door closed in front of us! Execute two-tier priority replanning
                    self.handle_blocked_path(next_pos)
                    break

                # Execute movement to next cell
                self.r, self.c = next_pos
                self.path_index += 1
                self.steps_taken += 1

                # Adversarial Door Action: If stepped through an open door, flick it!
                # Passed door immediately closes (0), opening its partner (1)
                toggled = self.world.on_agent_pass_door(self.r, self.c)
                if toggled and self.status == "OPENING_DOOR":
                    # Successfully opened the door! Recalculate fresh path to original goal
                    self.start_new_search()
                    break

                # Check key collection
                if self.pos in self.world.keys and self.pos not in self.collected_keys:
                    self.collected_keys = self.collected_keys | frozenset([self.pos])
                    # If this agent was moving towards a sub-goal, continue or replan if needed
                    if not self.finished and len(self.collected_keys) < len(self.world.keys):
                        self.start_new_search()
                        break

                # Check WIN / PASS condition: All 3 keys AND at exit
                if len(self.collected_keys) == len(self.world.keys) and self.pos == self.world.exit_pos:
                    self.finished = True
                    self.finish_time = current_time
                    self.status = "FINISHED"
                    return True

                # If current planned path segment finished without winning, start next search
                if self.path_index >= len(self.path):
                    self.path = []
                    if not self.finished:
                        self.start_new_search()
                    break

        return False

    def _is_path_passable(self) -> bool:
        """Checks if the remaining steps in current path are completely passable."""
        if not self.path:
            return True
        for i in range(self.path_index, len(self.path)):
            pr, pc = self.path[i]
            if not self.world.is_cell_passable(pr, pc):
                return False
        return True

