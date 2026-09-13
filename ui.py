"""
UI Module.
Draws the Top Bar with the prominent Timer, live agent telemetry table,
and the Winner overlay screen.
"""
import pygame
from typing import List, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TOP_BAR_HEIGHT, BOTTOM_PANEL_HEIGHT,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_TEXT_HEADER, COLOR_TIMER_ACCENT, DOOR_COLORS
)
from agent import Agent
from world import World

class UI:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_timer = pygame.font.SysFont("Consolas", 32, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_sub = pygame.font.SysFont("Arial", 12, bold=False)
        self.font_table_hdr = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_table = pygame.font.SysFont("Consolas", 11, bold=False)
        self.font_status = pygame.font.SysFont("Consolas", 10, bold=True)
        self.font_win_title = pygame.font.SysFont("Arial", 38, bold=True)
        self.font_win_sub = pygame.font.SysFont("Arial", 14, bold=False)

    def format_time(self, seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        centis = int((seconds * 100) % 100)
        return f"{mins:02d}:{secs:02d}.{centis:02d}"

    def draw_top_bar(self, elapsed_time: float, paused: bool, winner: Optional[Agent], move_speed: float, focus_idx: int):
        """Draws the prominent top timer and race status header."""
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, bar_rect)
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (0, TOP_BAR_HEIGHT), (SCREEN_WIDTH, TOP_BAR_HEIGHT), 1)

        # Left Section: Title and Mode
        title_surf = self.font_title.render("SEARCH ALGORITHM RACE", True, COLOR_TEXT_WHITE)
        self.screen.blit(title_surf, (16, 16))

        focus_str = "All Algorithms (0)" if focus_idx == 0 else f"Focus: #{focus_idx}"
        info_surf = self.font_sub.render(f"Mode: {focus_str}  |  Speed: {move_speed:.1f} cells/s", True, COLOR_TEXT_MUTED)
        self.screen.blit(info_surf, (16, 42))

        # Center Section: Large Timer
        time_str = self.format_time(elapsed_time)
        timer_col = (255, 200, 70) if paused else COLOR_TIMER_ACCENT
        timer_surf = self.font_timer.render(time_str, True, timer_col)
        timer_rect = timer_surf.get_rect(center=(SCREEN_WIDTH // 2, 34))
        self.screen.blit(timer_surf, timer_rect)

        sub_label = "PAUSED (SPACE)" if paused else ("COMPLETED" if winner else "RACE TIME")
        sub_col = (255, 100, 100) if paused else COLOR_TEXT_MUTED
        sub_surf = self.font_status.render(sub_label, True, sub_col)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        # Right Section: Status Indicator
        status_box = pygame.Rect(SCREEN_WIDTH - 150, 20, 134, 40)
        pygame.draw.rect(self.screen, (25, 27, 36), status_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, status_box, width=1, border_radius=6)

        if winner:
            st_text = f"WIN: {winner.name}"
            st_col = winner.color
        elif paused:
            st_text = "PAUSED"
            st_col = (255, 180, 50)
        else:
            st_text = "RACING"
            st_col = (60, 240, 120)

        st_surf = self.font_title.render(st_text, True, st_col)
        self.screen.blit(st_surf, st_surf.get_rect(center=status_box.center))

    def draw_bottom_panel(self, agents: List[Agent], world: World, focus_idx: int):
        """Draws the detailed real-time statistics panel for all 7 agents and doors."""
        start_y = SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT
        panel_rect = pygame.Rect(0, start_y, SCREEN_WIDTH, BOTTOM_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (0, start_y), (SCREEN_WIDTH, start_y), 1)

        # Global Door summary
        door_info_x = 16
        door_hdr = self.font_table_hdr.render("DOOR GATES:", True, COLOR_TEXT_HEADER)
        self.screen.blit(door_hdr, (door_info_x, start_y + 8))

        dx = door_info_x + 90
        for col_name in ["RED", "BLUE", "GREEN"]:
            d3_open = world.door_closed_state[col_name][3]
            d4_open = world.door_closed_state[col_name][4]
            is_unlocked = d3_open or d4_open
            stat_lbl = f"{col_name} (1,2: Open | 3,4: {'UNLOCKED' if is_unlocked else 'LOCKED'})"
            dot_col = (50, 230, 90) if is_unlocked else (240, 70, 70)
            
            # small status dot
            pygame.draw.circle(self.screen, dot_col, (dx, start_y + 16), 4)
            d_surf = self.font_status.render(stat_lbl, True, DOOR_COLORS[col_name])
            self.screen.blit(d_surf, (dx + 8, start_y + 10))
            dx += 225

        # Table Column Headers
        col_headers = [
            ("ALGORITHM", 16),
            ("KEYS", 130),
            ("POS", 185),
            ("STATUS", 255),
            ("EXPANDED", 360),
            ("GENERATED", 450),
            ("FRONTIER", 550),
            ("PATH", 645),
            ("REPLANS", 710)
        ]

        table_y = start_y + 32
        for title, x_pos in col_headers:
            h_surf = self.font_table_hdr.render(title, True, COLOR_TEXT_MUTED)
            self.screen.blit(h_surf, (x_pos, table_y))

        pygame.draw.line(self.screen, (35, 38, 50), (16, table_y + 16), (SCREEN_WIDTH - 16, table_y + 16), 1)

        # Agent Rows
        row_y = table_y + 22
        for idx, agent in enumerate(agents, 1):
            is_focused = (focus_idx == idx)
            bg_col = (28, 30, 42) if is_focused else None

            if bg_col:
                row_rect = pygame.Rect(12, row_y - 2, SCREEN_WIDTH - 24, 18)
                pygame.draw.rect(self.screen, bg_col, row_rect, border_radius=3)

            # Name with agent color
            name_text = f"{idx}. {agent.name}"
            name_surf = self.font_table_hdr.render(name_text, True, agent.color)
            self.screen.blit(name_surf, (16, row_y))

            # Keys
            k_count = len(agent.collected_keys)
            k_surf = self.font_table.render(f"{k_count}/3", True, (255, 215, 0) if k_count == 3 else COLOR_TEXT_WHITE)
            self.screen.blit(k_surf, (130, row_y))

            # Pos
            pos_surf = self.font_table.render(f"({agent.r:02d},{agent.c:02d})", True, COLOR_TEXT_WHITE)
            self.screen.blit(pos_surf, (185, row_y))

            # Status with indicator color
            status_colors = {
                "SEARCHING": (240, 180, 50),
                "MOVING": (60, 230, 120),
                "REPLANNING": (240, 90, 90),
                "TRAPPED": (200, 60, 60),
                "FINISHED": (100, 220, 255)
            }
            s_col = status_colors.get(agent.status, COLOR_TEXT_WHITE)
            stat_surf = self.font_status.render(agent.status, True, s_col)
            self.screen.blit(stat_surf, (255, row_y + 1))

            # Metrics
            exp_surf = self.font_table.render(f"{agent.total_expanded:6d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(exp_surf, (360, row_y))

            gen_surf = self.font_table.render(f"{agent.total_generated:6d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(gen_surf, (450, row_y))

            front_surf = self.font_table.render(f"{agent.last_frontier_size:4d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(front_surf, (550, row_y))

            path_len = len(agent.path)
            path_surf = self.font_table.render(f"{path_len:3d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(path_surf, (645, row_y))

            rep_surf = self.font_table.render(f"{agent.replans_count:2d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(rep_surf, (710, row_y))

            row_y += 19

        # Hotkey legend at bottom
        legend_text = "HOTKEYS: [R] Reset Maze  [SPACE] Pause  [TAB] Search Overlay  [1-7] Focus Agent  [0] Show All  [+/-] Speed  [ESC] Quit"
        leg_surf = self.font_sub.render(legend_text, True, (100, 105, 125))
        self.screen.blit(leg_surf, (16, SCREEN_HEIGHT - 22))

    def draw_winner_overlay(self, winner: Agent, elapsed_time: float):
        """Clean modal dialog displaying race winner and final statistics."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 15, 180))  # Translucent dark backdrop
        self.screen.blit(overlay, (0, 0))

        dialog_w, dialog_h = 440, 260
        dx = (SCREEN_WIDTH - dialog_w) // 2
        dy = (SCREEN_HEIGHT - dialog_h) // 2
        dialog_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        pygame.draw.rect(self.screen, (22, 24, 32), dialog_rect, border_radius=12)
        pygame.draw.rect(self.screen, winner.color, dialog_rect, width=2, border_radius=12)

        # Title
        win_title = self.font_win_title.render(f"{winner.name} WINS!", True, winner.color)
        self.screen.blit(win_title, win_title.get_rect(center=(SCREEN_WIDTH // 2, dy + 45)))

        sub = self.font_win_sub.render("ALL 3 KEYS COLLECTED & EXIT REACHED", True, (240, 245, 250))
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, dy + 82)))

        # Summary box
        stat_box = pygame.Rect(dx + 30, dy + 110, dialog_w - 60, 85)
        pygame.draw.rect(self.screen, (15, 16, 22), stat_box, border_radius=6)
        pygame.draw.rect(self.screen, (40, 44, 56), stat_box, width=1, border_radius=6)

        stats = [
            f"Race Time: {self.format_time(elapsed_time)}",
            f"Nodes Expanded: {winner.total_expanded}  |  Generated: {winner.total_generated}",
            f"Path Length: {len(winner.path)}  |  Re-plans Triggered: {winner.replans_count}"
        ]
        for i, text in enumerate(stats):
            t_surf = self.font_table_hdr.render(text, True, (200, 205, 220))
            self.screen.blit(t_surf, (dx + 45, dy + 122 + i * 22))

        restart_text = self.font_sub.render("Press [R] to Generate a New Race  |  [ESC] to Quit", True, (130, 140, 165))
        self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, dy + 225)))
