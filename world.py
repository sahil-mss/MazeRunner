"""
Global World Model:
Handles keys, exit, and the shared 9-door dynamic mechanism.
Guarantees full initial reachability while maintaining dynamic adversarial effects.
"""
import random
from config import ROWS, COLS
from maze import Maze

class Door:
    def __init__(self, r: int, c: int, color: str, number: int):
        self.r = r
        self.c = c
        self.color = color      # "RED", "BLUE", or "GREEN"
        self.number = number    # 1, 2, 3, or 4

    @property
    def pos(self):
        return (self.r, self.c)

class World:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.start_pos = (0, 0)
        self.exit_pos = (0, 0)
        self.keys = []     # List of (r, c)
        self.doors = []    # List of Door objects
        self.door_map = {} # (r, c) -> Door

        # Global door state per color:
        # Doors 1 & 2: Always open (act as switches).
        # Doors 3 & 4: Closed initially (False).
        self.door_closed_state = {
            "RED": {3: False, 4: False},
            "BLUE": {3: False, 4: False},
            "GREEN": {3: False, 4: False}
        }

        # Revision counter to notify agents when world changes
        self.revision = 0
        self.setup_world()

    def _get_reachable_cells(self, start_pos, check_closed_doors=True):
        """Returns set of reachable cells from start_pos considering door states."""
        visited = {start_pos}
        queue = [start_pos]
        for curr in queue:
            for nxt in self.maze.get_neighbors(curr[0], curr[1]):
                if nxt not in visited:
                    if not check_closed_doors or self.is_door_passable(nxt[0], nxt[1]):
                        visited.add(nxt)
                        queue.append(nxt)
        return visited

    def setup_world(self):
        self.start_pos = (0, 0)
        all_cells = self.maze.get_all_cells()
        colors = ["RED", "BLUE", "GREEN"]

        # Loop until a configuration is generated where:
        # - Keys are placed behind Door 3/4
        # - Exit and open doors 1 & 2 are reachable from Start
        # - When Doors 3 & 4 open, keys become fully reachable
        for attempt in range(200):
            self.reset_doors()
            used = {self.start_pos}

            # 1. Exit cell: placed far from Start in open area
            cells_by_dist = sorted(
                all_cells,
                key=lambda p: self.maze.shortest_path_dist(self.start_pos, p),
                reverse=True
            )
            self.exit_pos = cells_by_dist[0]
            used.add(self.exit_pos)

            # Find dead-end or chamber cells for keys
            dead_ends = [
                p for p in all_cells
                if len(self.maze.get_neighbors(p[0], p[1])) == 1
                and p != self.start_pos and p != self.exit_pos
            ]
            random.shuffle(dead_ends)

            other_candidates = [
                p for p in all_cells
                if p not in used and p != self.start_pos and p != self.exit_pos
            ]
            random.shuffle(other_candidates)

            # Select 3 key positions
            key_positions = []
            for _ in range(3):
                if dead_ends:
                    k_pos = dead_ends.pop()
                elif other_candidates:
                    k_pos = other_candidates.pop()
                else:
                    break
                key_positions.append(k_pos)
                used.add(k_pos)

            if len(key_positions) < 3:
                continue

            self.keys = key_positions

            # Place 4 doors for each of the 3 colors:
            # Door 1: Open switch
            # Door 2: Open switch
            # Door 3: Closed gate (guarding the key's entrance)
            # Door 4: Closed gate (secondary gate / alternate route)
            self.doors = []
            self.door_map = {}

            door_placement_success = True
            remaining_free = [p for p in all_cells if p not in used and p != self.start_pos and p != self.exit_pos]
            random.shuffle(remaining_free)

            for idx, color in enumerate(colors):
                key_pos = self.keys[idx]
                key_neighbors = self.maze.get_neighbors(key_pos[0], key_pos[1])
                door3_pos = None

                # Find a neighbor cell of the key to place Door 3 (directly gating the key)
                for kn in key_neighbors:
                    if kn not in used and kn != self.start_pos and kn != self.exit_pos:
                        door3_pos = kn
                        break

                if not door3_pos and remaining_free:
                    door3_pos = remaining_free.pop()

                if not door3_pos:
                    door_placement_success = False
                    break

                used.add(door3_pos)
                d3 = Door(door3_pos[0], door3_pos[1], color, 3)
                self.doors.append(d3)
                self.door_map[door3_pos] = d3

                # Door 4 (another closed gate for this color)
                if not remaining_free:
                    door_placement_success = False
                    break
                door4_pos = remaining_free.pop()
                used.add(door4_pos)
                d4 = Door(door4_pos[0], door4_pos[1], color, 4)
                self.doors.append(d4)
                self.door_map[door4_pos] = d4

                # Door 1 & Door 2 (open switch doors for this color)
                if len(remaining_free) < 2:
                    door_placement_success = False
                    break
                door1_pos = remaining_free.pop()
                used.add(door1_pos)
                d1 = Door(door1_pos[0], door1_pos[1], color, 1)
                self.doors.append(d1)
                self.door_map[door1_pos] = d1

                door2_pos = remaining_free.pop()
                used.add(door2_pos)
                d2 = Door(door2_pos[0], door2_pos[1], color, 2)
                self.doors.append(d2)
                self.door_map[door2_pos] = d2

            if not door_placement_success:
                continue

            # Verify initial connectivity:
            # - Start can reach all open doors (1 & 2) and Exit
            initial_reachable = self._get_reachable_cells(self.start_pos, check_closed_doors=True)
            all_switches_reachable = all(
                d.pos in initial_reachable for d in self.doors if d.number in (1, 2)
            )

            # Test reachability when doors 3 & 4 are opened
            for c in colors:
                self.door_closed_state[c][3] = True
                self.door_closed_state[c][4] = True

            unlocked_reachable = self._get_reachable_cells(self.start_pos, check_closed_doors=True)
            all_keys_reachable_when_unlocked = all(k in unlocked_reachable for k in self.keys)

            self.reset_doors()

            if all_switches_reachable and all_keys_reachable_when_unlocked and self.exit_pos in initial_reachable:
                break

        self.reset_doors()

    def reset_doors(self):
        self.door_closed_state = {
            "RED": {3: False, 4: False},
            "BLUE": {3: False, 4: False},
            "GREEN": {3: False, 4: False}
        }
        self.revision += 1

    def is_door_passable(self, r: int, c: int, allow_closed: bool = False) -> bool:
        """Returns True if the cell is not a closed door (or allow_closed is True)."""
        door = self.door_map.get((r, c))
        if not door:
            return True
        if door.number in (1, 2):
            return True
        # Door 3 or 4: passable if open or if hypothetical search path planning allows it
        if allow_closed:
            return True
        return self.door_closed_state[door.color][door.number]

    def on_agent_enter_cell(self, r: int, c: int) -> bool:
        """
        Triggered when an agent steps into a cell.
        If the cell is an open door (Door 1 or 2), it opens Door 3 & 4 of that color.
        If the cell is Door 3 or 4, passing through closes it again.
        Returns True if the world changed (requiring other agents to re-check).
        """
        door = self.door_map.get((r, c))
        if not door:
            return False

        changed = False
        color = door.color
        if door.number in (1, 2):
            # Passing through open Door 1 or 2 OPENS closed Door 3 and Door 4
            if not self.door_closed_state[color][3] or not self.door_closed_state[color][4]:
                self.door_closed_state[color][3] = True
                self.door_closed_state[color][4] = True
                changed = True
        elif door.number in (3, 4):
            # Door 3 & 4 remain open once unlocked by switches so agents can retrieve keys and return safely
            pass

        if changed:
            self.revision += 1
        return changed

    def get_valid_neighbors(self, r: int, c: int, allow_hypothetical: bool = True):
        """
        Returns adjacent reachable cells considering maze walls
        and doors (with allow_hypothetical allowing future planned traversal through closed doors).
        """
        neighbors = []
        for nr, nc in self.maze.get_neighbors(r, c):
            if self.is_door_passable(nr, nc, allow_closed=allow_hypothetical):
                neighbors.append((nr, nc))
        return neighbors
