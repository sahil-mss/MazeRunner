"""
Global World Model:
Handles keys, exit, and two alternating doors of three colors each (RED, BLUE, GREEN).
For each color, exactly one door is open (1) and the other is closed (0), alternating periodically or upon trigger.
"""
import random
from typing import Dict, Tuple, List, Optional
from config import ROWS, COLS, DOOR_TOGGLE_INTERVAL
from maze import Maze

class Door:
    def __init__(self, r: int, c: int, color: str, door_id: int):
        self.r = r
        self.c = c
        self.color = color      # "RED", "BLUE", or "GREEN"
        self.door_id = door_id  # 1 or 2

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.r, self.c)

class World:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.start_pos = (0, 0)
        self.exit_pos = (0, 0)
        self.keys: List[Tuple[int, int]] = []
        self.doors: List[Door] = []
        self.door_map: Dict[Tuple[int, int], Door] = {}
        
        # For each color, True means Door 1 is OPEN (1) & Door 2 is CLOSED (0).
        # False means Door 1 is CLOSED (0) & Door 2 is OPEN (1).
        # Guaranteed always either (1, 0) or (0, 1).
        self.color_phase: Dict[str, bool] = {
            "RED": True,
            "BLUE": False,
            "GREEN": True
        }
        
        self.toggle_timer = 0.0
        self.revision = 0
        self.setup_world()

    def setup_world(self):
        self.start_pos = (0, 0)
        all_cells = self.maze.get_all_cells()
        colors = ["RED", "BLUE", "GREEN"]

        for _ in range(200):
            # 1. Exit cell: placed far from Start
            cells_by_dist = sorted(
                all_cells,
                key=lambda p: self.maze.shortest_path_dist(self.start_pos, p),
                reverse=True
            )
            self.exit_pos = cells_by_dist[0]
            used = {self.start_pos, self.exit_pos}

            # 2. Select 3 key positions across the maze
            dead_ends = [
                p for p in all_cells
                if len(self.maze.get_neighbors(p[0], p[1])) == 1
                and p not in used
            ]
            random.shuffle(dead_ends)

            other_candidates = [
                p for p in all_cells
                if p not in used
            ]
            random.shuffle(other_candidates)

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

            # 3. Select 2 distinct doors for each of the 3 colors (6 doors total)
            # Choose cells that have at least 2 neighbors (passageways/corridors)
            corridor_cells = [
                p for p in all_cells
                if p not in used and len(self.maze.get_neighbors(p[0], p[1])) >= 2
            ]
            random.shuffle(corridor_cells)

            if len(corridor_cells) < 6:
                continue

            self.doors = []
            self.door_map = {}

            door_placed_successfully = True
            for color in colors:
                d1_pos = corridor_cells.pop()
                used.add(d1_pos)
                d1 = Door(d1_pos[0], d1_pos[1], color, 1)

                d2_pos = corridor_cells.pop()
                used.add(d2_pos)
                d2 = Door(d2_pos[0], d2_pos[1], color, 2)

                self.doors.extend([d1, d2])
                self.door_map[d1_pos] = d1
                self.door_map[d2_pos] = d2

            # Validate that every key and the exit have unobstructed active paths
            test_phases = [
                {"RED": True, "BLUE": False, "GREEN": True},
                {"RED": False, "BLUE": True, "GREEN": False}
            ]
            valid_reachability = True
            for ph in test_phases:
                visited = {self.start_pos}
                queue = [self.start_pos]
                for curr in queue:
                    for nxt in self.maze.get_neighbors(curr[0], curr[1]):
                        if nxt not in visited:
                            d = self.door_map.get(nxt)
                            is_open = True
                            if d is not None:
                                phase = ph[d.color]
                                is_open = phase if d.door_id == 1 else (not phase)
                            if is_open:
                                visited.add(nxt)
                                queue.append(nxt)

                if not (self.exit_pos in visited and all(k in visited for k in self.keys)):
                    valid_reachability = False
                    break

            if valid_reachability and door_placed_successfully:
                break

        self.color_phase = {
            "RED": True,
            "BLUE": False,
            "GREEN": True
        }
        self.toggle_timer = 0.0
        self.revision += 1

    def is_door_open(self, door: Door) -> bool:
        """Returns True if the door is open (1), False if closed (0)."""
        phase = self.color_phase[door.color]
        if door.door_id == 1:
            return phase      # 1 if True, 0 if False
        else:
            return not phase  # 0 if True, 1 if False

    def is_cell_passable(self, r: int, c: int) -> bool:
        """Returns True if cell has no door or its door is currently open."""
        door = self.door_map.get((r, c))
        if not door:
            return True
        return self.is_door_open(door)

    def toggle_color(self, color: str):
        """Toggles the phase of the given color: (1, 0) becomes (0, 1) and vice-versa."""
        self.color_phase[color] = not self.color_phase[color]
        self.revision += 1

    def get_partner_door(self, door: Door) -> Optional[Door]:
        """Returns the other door of the same color."""
        partner_id = 2 if door.door_id == 1 else 1
        for d in self.doors:
            if d.color == door.color and d.door_id == partner_id:
                return d
        return None

    def on_agent_pass_door(self, r: int, c: int) -> bool:
        """
        Triggered when an agent steps through an open door.
        Toggles that color pair so the passed door closes and its partner opens.
        Returns True if a toggle occurred.
        """
        door = self.door_map.get((r, c))
        if door is not None and self.is_door_open(door):
            self.toggle_color(door.color)
            return True
        return False

    def get_valid_neighbors(self, r: int, c: int, allow_hypothetical: bool = True):
        """
        Returns adjacent reachable cells considering maze walls
        and physical door states (if allow_hypothetical is False, closed doors are blocked).
        """
        neighbors = []
        for nr, nc in self.maze.get_neighbors(r, c):
            if allow_hypothetical or self.is_cell_passable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

