"""
Renderer Module.
Renders classical maze with thin wall lines, keys, doors, agents, and search overlays.
"""
import pygame
from typing import List, Optional
from config import (
    TILE_SIZE, ROWS, COLS, TOP_BAR_HEIGHT,
    COLOR_BG, COLOR_WALL, COLOR_KEY, COLOR_EXIT, COLOR_START,
    DOOR_COLORS, COLOR_TEXT_MUTED
)
from world import World
from agent import Agent

class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_tiny = pygame.font.SysFont("Consolas", 10, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 12, bold=True)

    def grid_to_screen(self, r: int, c: int):
        x = c * TILE_SIZE
        y = TOP_BAR_HEIGHT + r * TILE_SIZE
        return x, y

    def draw_maze_lines(self, world: World):
        """
        Draws classical thin white lines for maze walls.
        Corridors remain pure dark background.
        """
        maze = world.maze
        line_color = COLOR_WALL
        line_width = 2

        # Draw interior and boundary walls
        for r in range(maze.rows):
            for c in range(maze.cols):
                x, y = self.grid_to_screen(r, c)
                walls = maze.cells[r][c]

                # Top wall (only draw if cell has top wall and (r==0 or not drawn by upper neighbor))
                if walls[0] and r == 0:
                    pygame.draw.line(self.screen, line_color, (x, y), (x + TILE_SIZE, y), line_width)
                # Right wall
                if walls[1]:
                    pygame.draw.line(self.screen, line_color, (x + TILE_SIZE, y), (x + TILE_SIZE, y + TILE_SIZE), line_width)
                # Bottom wall
                if walls[2]:
                    pygame.draw.line(self.screen, line_color, (x, y + TILE_SIZE), (x + TILE_SIZE, y + TILE_SIZE), line_width)
                # Left wall (only draw if cell has left wall and c==0)
                if walls[3] and c == 0:
                    pygame.draw.line(self.screen, line_color, (x, y), (x, y + TILE_SIZE), line_width)

    def draw_start_and_exit(self, world: World):
        # Draw Start Marker
        sx, sy = self.grid_to_screen(world.start_pos[0], world.start_pos[1])
        s_rect = pygame.Rect(sx + 3, sy + 3, TILE_SIZE - 6, TILE_SIZE - 6)
        pygame.draw.rect(self.screen, (25, 45, 75), s_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_START, s_rect, width=1, border_radius=4)
        s_text = self.font_small.render("S", True, COLOR_START)
        self.screen.blit(s_text, s_text.get_rect(center=s_rect.center))

        # Draw Exit Marker
        ex, ey = self.grid_to_screen(world.exit_pos[0], world.exit_pos[1])
        e_rect = pygame.Rect(ex + 2, ey + 2, TILE_SIZE - 4, TILE_SIZE - 4)
        pygame.draw.rect(self.screen, (15, 60, 35), e_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_EXIT, e_rect, width=2, border_radius=4)
        e_text = self.font_tiny.render("EXIT", True, COLOR_EXIT)
        self.screen.blit(e_text, e_text.get_rect(center=e_rect.center))

    def draw_keys(self, world: World):
        """Draw glowing diamond keys with index label."""
        for idx, (kr, kc) in enumerate(world.keys, 1):
            kx, ky = self.grid_to_screen(kr, kc)
            cx, cy = kx + TILE_SIZE // 2, ky + TILE_SIZE // 2
            
            # Diamond vertices
            radius = 7
            pts = [
                (cx, cy - radius),
                (cx + radius, cy),
                (cx, cy + radius),
                (cx - radius, cy)
            ]
            # Outer glow
            pygame.draw.polygon(self.screen, (120, 100, 0), pts)
            pygame.draw.polygon(self.screen, COLOR_KEY, pts, width=2)
            
            label = self.font_tiny.render(str(idx), True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=(cx, cy)))

    def draw_doors(self, world: World):
        """
        Draws the 6 colored doors (2 per color: RED, BLUE, GREEN).
        Shows clear binary state:
        - Open (1): Hollow glowing frame with colored border and '1' / 'OPEN' indicator.
        - Closed (0): Solid colored barrier with cross / hatch and '0' / 'LOCK' indicator.
        """
        for door in world.doors:
            x, y = self.grid_to_screen(door.r, door.c)
            base_col = DOOR_COLORS[door.color]
            is_open = world.is_door_open(door)

            rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
            lbl_text = f"D{door.door_id}"
            if is_open:
                # Open Door (1): Accessible passageway with glowing portal frame
                pygame.draw.rect(self.screen, (20, 35, 28), rect, border_radius=4)
                pygame.draw.rect(self.screen, base_col, rect, width=2, border_radius=4)
                txt = self.font_tiny.render(lbl_text, True, base_col)
                self.screen.blit(txt, txt.get_rect(center=rect.center))
            else:
                # Closed Door (0): Solid impassable barrier
                pygame.draw.rect(self.screen, base_col, rect, border_radius=4)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, width=1, border_radius=4)
                txt = self.font_tiny.render(lbl_text, True, (20, 20, 20))
                self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_search_visualization(self, agents: List[Agent], focus_idx: int):
        """
        Draws search exploration: subtle dots for explored nodes,
        thin boxes for frontier, and thin line for current plan.
        """
        target_agents = [agents[focus_idx - 1]] if focus_idx > 0 else agents

        for agent in target_agents:
            if agent.search_instance is None:
                continue

            # Explored nodes (subtle, tiny dots)
            for state in agent.search_instance.explored_states[-150:]:
                x, y = self.grid_to_screen(state.r, state.c)
                cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                pygame.draw.circle(self.screen, (40, 42, 55), (cx, cy), 2)

            # Frontier nodes (dim colored outlines)
            for f_state in agent.search_instance.frontier_states[-30:]:
                fx, fy = self.grid_to_screen(f_state.r, f_state.c)
                f_rect = pygame.Rect(fx + 5, fy + 5, TILE_SIZE - 10, TILE_SIZE - 10)
                pygame.draw.rect(self.screen, (70, 75, 95), f_rect, width=1)

            # Planned Path line
            if agent.path and len(agent.path) > 1:
                pts = [
                    (self.grid_to_screen(p[0], p[1])[0] + TILE_SIZE // 2,
                     self.grid_to_screen(p[0], p[1])[1] + TILE_SIZE // 2)
                    for p in agent.path[agent.path_index:]
                ]
                if len(pts) >= 2:
                    # Draw path with agent color slightly dimmed
                    dimmed_col = (agent.color[0] // 2, agent.color[1] // 2, agent.color[2] // 2)
                    pygame.draw.lines(self.screen, dimmed_col, False, pts, 2)

    def draw_agents(self, agents: List[Agent], focus_idx: int):
        """
        Draws the 7 competing agents.
        If multiple agents occupy the same cell, distribute their positions smoothly.
        """
        # Group agents by current cell
        cell_map = {}
        for idx, agent in enumerate(agents, 1):
            if focus_idx != 0 and idx != focus_idx:
                continue
            cell_map.setdefault(agent.pos, []).append(agent)

        # Offsets for up to 7 overlapping agents in one cell
        offsets = [
            (0, 0),
            (-5, -5), (5, -5),
            (-5, 5), (5, 5),
            (0, -6), (0, 6)
        ]

        for pos, group in cell_map.items():
            base_x, base_y = self.grid_to_screen(pos[0], pos[1])
            cx = base_x + TILE_SIZE // 2
            cy = base_y + TILE_SIZE // 2

            for i, agent in enumerate(group):
                if len(group) == 1:
                    ax, ay = cx, cy
                else:
                    ox, oy = offsets[i % len(offsets)]
                    ax, ay = cx + ox, cy + oy

                # Outer circle
                radius = 6 if len(group) > 1 else 7
                pygame.draw.circle(self.screen, agent.color, (ax, ay), radius)
                # Shiny inner core
                pygame.draw.circle(self.screen, (255, 255, 255), (ax, ay), 2)
                
                # If agent is finished, draw winner crown glow
                if agent.finished:
                    pygame.draw.circle(self.screen, (255, 255, 255), (ax, ay), radius + 3, width=1)
