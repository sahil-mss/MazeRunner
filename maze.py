"""
Classical Maze Generator.
Uses recursive backtracking to generate a perfect maze.
Walls between cells are stored explicitly so they can be rendered as thin lines.
"""
import random
from collections import deque

class Maze:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # Each cell has 4 wall flags: [Top, Right, Bottom, Left]
        # Initially all walls exist.
        self.cells = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
        self.generate()

    def generate(self):
        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        stack = [(0, 0)]
        visited[0][0] = True

        directions = [
            (-1, 0, 0, 2),  # Up: dr, dc, current_wall_idx, neighbor_wall_idx
            (0, 1, 1, 3),   # Right
            (1, 0, 2, 0),   # Down
            (0, -1, 3, 1)   # Left
        ]

        while stack:
            r, c = stack[-1]
            unvisited_neighbors = []

            for dr, dc, wall_curr, wall_next in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and not visited[nr][nc]:
                    unvisited_neighbors.append((nr, nc, wall_curr, wall_next))

            if unvisited_neighbors:
                nr, nc, wall_curr, wall_next = random.choice(unvisited_neighbors)
                # Knock down wall between current and chosen neighbor
                self.cells[r][c][wall_curr] = False
                self.cells[nr][nc][wall_next] = False
                visited[nr][nc] = True
                stack.append((nr, nc))
            else:
                stack.pop()

        # Add small braided loops (about 4% of interior walls removed)
        # to ensure multiple interesting alternative routes for racing agents!
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if random.random() < 0.04:
                    if random.random() < 0.5:
                        self.cells[r][c][1] = False
                        self.cells[r][c + 1][3] = False
                    else:
                        self.cells[r][c][2] = False
                        self.cells[r + 1][c][0] = False

    def can_move(self, r: int, c: int, dr: int, dc: int) -> bool:
        """Returns True if there is no physical maze wall between (r,c) and (r+dr, c+dc)."""
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return False

        if dr == -1 and dc == 0:
            return not self.cells[r][c][0]
        elif dr == 0 and dc == 1:
            return not self.cells[r][c][1]
        elif dr == 1 and dc == 0:
            return not self.cells[r][c][2]
        elif dr == 0 and dc == -1:
            return not self.cells[r][c][3]
        return False

    def get_neighbors(self, r: int, c: int):
        """Returns all physically adjacent cells without walls."""
        res = []
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            if self.can_move(r, c, dr, dc):
                res.append((r + dr, c + dc))
        return res

    def get_all_cells(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)]

    def shortest_path_dist(self, start_pos, target_pos):
        """BFS distance calculation between any two cells in the static maze."""
        if start_pos == target_pos:
            return 0
        visited = {start_pos}
        queue = deque([(start_pos, 0)])
        while queue:
            pos, dist = queue.popleft()
            if pos == target_pos:
                return dist
            for nxt in self.get_neighbors(pos[0], pos[1]):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, dist + 1))
        return 999999
