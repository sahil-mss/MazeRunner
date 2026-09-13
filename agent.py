"""
Agent class.
Encapsulates an AI agent, its search algorithm, physical position, collected keys,
re-planning triggers, and responsive movement timers.
When blocked by closed doors, agents dynamically calculate alternative routes
to other accessible keys or to door switches to open locked paths.
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
        self.status = "SEARCHING"  # "SEARCHING", "MOVING", "REPLANNING", "TRAPPED", "FINISHED"

        # Movement path and execution
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.move_accumulator = 0.0

        # Telemetry & Re-planning
        self.search_instance = None
        self.last_world_revision = -1
        self.replans_count = 0
        self.total_expanded = 0
        self.total_generated = 0
        self.last_frontier_size = 0

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

    def calculate_alternative_route(self, blocked_pos: Optional[Tuple[int, int]] = None) -> bool:
        """
        When stuck or blocked by a closed door:
        1. Look for another uncollected key that is currently reachable.
        2. If no key is directly reachable, calculate a path to an open switch door (Door 1 or 2)
           prioritizing the color of the blocked door or remaining keys to unlock them.
        Returns True if an alternative route was found and set, False otherwise.
        """
        remaining_keys = [k for k in self.world.keys if k not in self.collected_keys]

        # 1. First priority: Calculate route to another uncollected key that is open and passable
        key_candidates = []
        for k in remaining_keys:
            kp = self._bfs_passable_path(self.pos, k)
            if kp and len(kp) > 1:
                key_candidates.append((len(kp), kp))
        if key_candidates:
            key_candidates.sort(key=lambda x: x[0])
            self.path = key_candidates[0][1]
            self.path_index = 0
            self.status = "MOVING"
            return True

        # 2. Second priority: Find reachable switch doors (Door 1 or Door 2) to open locked doors
        blocked_door = self.world.door_map.get(blocked_pos) if blocked_pos else None
        blocked_color = blocked_door.color if blocked_door else None

        # Determine which colors are still needed for uncollected keys
        needed_colors = {
            col for i, col in enumerate(["RED", "BLUE", "GREEN"])
            if i < len(self.world.keys) and self.world.keys[i] in remaining_keys
        }

        # Build candidate switches grouped by priority:
        # Priority 0: Switch for the door that directly blocked us
        # Priority 1: Switch for a key that has not yet been collected and whose gates (Door 3/4) are still closed
        # Priority 2: Any other reachable switch
        priority_buckets = {0: [], 1: [], 2: []}
        for p, d in self.world.door_map.items():
            if d.number in (1, 2):
                if blocked_color and d.color == blocked_color:
                    priority_buckets[0].append(p)
                elif d.color in needed_colors and (not self.world.door_closed_state[d.color][3] or not self.world.door_closed_state[d.color][4]):
                    priority_buckets[1].append(p)
                else:
                    priority_buckets[2].append(p)

        for prio in [0, 1, 2]:
            bucket_paths = []
            for sw_pos in priority_buckets[prio]:
                sp = self._bfs_passable_path(self.pos, sw_pos)
                if sp and len(sp) > 1:
                    bucket_paths.append((len(sp), sp))
            if bucket_paths:
                bucket_paths.sort(key=lambda x: x[0])
                self.path = bucket_paths[0][1]
                self.path_index = 0
                self.status = "MOVING"
                return True

        return False

    def update(self, dt: float, move_speed: float) -> bool:
        """
        Updates search and movement incrementally.
        dt: delta time in seconds.
        move_speed: cells per second.
        Returns True if this agent reached the winning condition on this update.
        """
        if self.finished:
            self.status = "FINISHED"
            return False

        # 1. Environment Change Detection:
        # If doors changed, check if our upcoming path is blocked
        if self.world.revision != self.last_world_revision:
            self.last_world_revision = self.world.revision
            if self.path and not self._is_upcoming_path_valid():
                self.replans_count += 1
                self.status = "REPLANNING"
                # Check for alternative route immediately
                first_blocked = None
                for pr, pc in self.path[self.path_index:]:
                    if not self.world.is_door_passable(pr, pc):
                        first_blocked = (pr, pc)
                        break
                if not self.calculate_alternative_route(first_blocked):
                    self.start_new_search()

        # 2. Search Execution (if path not yet found):
        if not self.path:
            if self.search_instance is not None and not self.search_instance.is_finished():
                self.status = "SEARCHING"
                # Expand a bounded number of nodes per frame to NEVER freeze the UI
                self.search_instance.step(MAX_SEARCH_STEPS_PER_FRAME)
                
                # Update live stats
                self.total_expanded = self.search_instance.expanded_count
                self.total_generated = self.search_instance.generated_count
                self.last_frontier_size = len(self.search_instance.frontier_states)

                if self.search_instance.is_finished():
                    if self.search_instance.success:
                        self.path = self.search_instance.get_path()
                        self.path_index = 0
                        self.status = "MOVING"
                    else:
                        # Search exhausted without finding path (currently trapped behind doors)
                        self.replans_count += 1
                        if not self.calculate_alternative_route():
                            self.status = "TRAPPED"
            elif self.status == "TRAPPED":
                # When trapped, try to calculate an alternative route periodically
                self.move_accumulator += dt
                if self.move_accumulator > 0.3:
                    self.move_accumulator = 0.0
                    if not self.calculate_alternative_route():
                        self.start_new_search()
                return False

        # 3. Responsive Movement (moving cell by cell):
        if self.path and self.path_index < len(self.path):
            self.status = "MOVING"
            self.move_accumulator += dt
            step_interval = 1.0 / move_speed

            while self.move_accumulator >= step_interval:
                self.move_accumulator -= step_interval
                
                # Next step coordinate
                next_pos = self.path[self.path_index]
                
                # If path starts at current position, advance to the next
                if next_pos == self.pos:
                    self.path_index += 1
                    if self.path_index >= len(self.path):
                        self.path = []
                        break
                    next_pos = self.path[self.path_index]

                # Validate whether the next cell is physically passable right now
                if not self.world.is_door_passable(next_pos[0], next_pos[1]):
                    # Door closed in front of us! Must replan and calculate alternative route
                    self.replans_count += 1
                    self.status = "REPLANNING"
                    if not self.calculate_alternative_route(next_pos):
                        self.start_new_search()
                    break

                # Execute movement to next cell
                self.r, self.c = next_pos
                self.path_index += 1

                # Check key collection
                if self.pos in self.world.keys and self.pos not in self.collected_keys:
                    self.collected_keys = self.collected_keys | frozenset([self.pos])
                    # If this agent was moving towards a sub-goal, start fresh search towards remaining goals
                    if not self.finished and len(self.collected_keys) < len(self.world.keys):
                        self.start_new_search()
                        break

                # Check door interaction (switches/gates)
                world_changed = self.world.on_agent_enter_cell(self.r, self.c)
                if world_changed:
                    # Environment changed globally!
                    self.last_world_revision = self.world.revision
                    # If we stepped on an open switch door, start fresh full search now that gates opened
                    door = self.world.door_map.get(self.pos)
                    if door and door.number in (1, 2):
                        self.start_new_search()
                        break

                # Check WIN condition: All 3 keys AND at exit
                if len(self.collected_keys) == len(self.world.keys) and self.pos == self.world.exit_pos:
                    self.finished = True
                    self.status = "FINISHED"
                    return True

                # If we exhausted our current plan segment, trigger next search step
                if self.path_index >= len(self.path):
                    self.path = []
                    if not self.finished:
                        self.start_new_search()
                    break

        return False

    def _is_upcoming_path_valid(self) -> bool:
        """Verifies if remaining steps in current path do not cross closed doors."""
        if not self.path:
            return True
        for i in range(self.path_index, len(self.path)):
            pr, pc = self.path[i]
            if not self.world.is_door_passable(pr, pc):
                return False
        return True
