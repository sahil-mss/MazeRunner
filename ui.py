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
    COLOR_TEXT_HEADER, COLOR_TIMER_ACCENT, COLOR_KEY, DOOR_COLORS
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
        self.font_win_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_win_sub = pygame.font.SysFont("Arial", 13, bold=False)
        self.font_rank = pygame.font.SysFont("Arial", 13, bold=True)

    def format_time(self, seconds: Optional[float]) -> str:
        if seconds is None:
            return "--:--.--"
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        centis = int((seconds * 100) % 100)
        return f"{mins:02d}:{secs:02d}.{centis:02d}"

    def draw_top_bar(self, elapsed_time: float, paused: bool, all_finished: bool, winner: Optional[Agent], move_speed: float, focus_idx: int):
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

        sub_label = "PAUSED (SPACE)" if paused else ("ALL FINISHED!" if all_finished else ("LEADER: " + winner.name if winner else "RACE TIME"))
        sub_col = (255, 100, 100) if paused else ((100, 255, 150) if all_finished else COLOR_TEXT_MUTED)
        sub_surf = self.font_status.render(sub_label, True, sub_col)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        # Right Section: Status Indicator
        status_box = pygame.Rect(SCREEN_WIDTH - 155, 20, 140, 40)
        pygame.draw.rect(self.screen, (25, 27, 36), status_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, status_box, width=1, border_radius=6)

        if all_finished:
            st_text = "COMPLETE"
            st_col = (255, 215, 0)
        elif winner:
            st_text = f"1ST: {winner.name}"
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
        """Draws the live telemetry panel comparing all algorithms."""
        start_y = SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT
        panel_rect = pygame.Rect(0, start_y, SCREEN_WIDTH, BOTTOM_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, COLOR_PANEL_BORDER, (0, start_y), (SCREEN_WIDTH, start_y), 1)

        # Panel Header / Mission Objectives & Live Door States
        door_lbl = self.font_table_hdr.render("DOORS (1=OPEN, 0=CLOSED):", True, COLOR_TEXT_HEADER)
        self.screen.blit(door_lbl, (16, start_y + 8))

        dx = 190
        for cname in ["RED", "BLUE", "GREEN"]:
            p = world.color_phase[cname]
            d1_st = "1" if p else "0"
            d2_st = "0" if p else "1"
            txt = f"{cname}: [{d1_st}, {d2_st}]"
            col = DOOR_COLORS[cname]
            surf = self.font_status.render(txt, True, col)
            self.screen.blit(surf, (dx, start_y + 9))
            dx += 110

        # Finished summary count
        fin_count = sum(1 for a in agents if a.finished)
        fin_text = f"Finished: {fin_count}/{len(agents)}"
        fin_surf = self.font_table_hdr.render(fin_text, True, (255, 215, 0) if fin_count == len(agents) else COLOR_TIMER_ACCENT)
        self.screen.blit(fin_surf, (SCREEN_WIDTH - 120, start_y + 8))

        # Table Column Headers
        col_headers = [
            ("ALGORITHM", 16),
            ("KEYS", 125),
            ("POS", 175),
            ("STATUS", 240),
            ("EXPANDED", 335),
            ("GENERATED", 420),
            ("FRONTIER", 510),
            ("PATH", 605),
            ("REPLANS", 670)
        ]

        table_y = start_y + 30
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
            self.screen.blit(k_surf, (125, row_y))

            # Pos
            pos_surf = self.font_table.render(f"({agent.r:02d},{agent.c:02d})", True, COLOR_TEXT_WHITE)
            self.screen.blit(pos_surf, (175, row_y))

            # Status with indicator color
            status_colors = {
                "SEARCHING": (240, 180, 50),
                "MOVING": (60, 230, 120),
                "REPLANNING": (255, 85, 85),
                "OPENING_DOOR": (180, 120, 255),
                "FINISHED": (100, 220, 255)
            }
            s_col = status_colors.get(agent.status, COLOR_TEXT_WHITE)
            stat_surf = self.font_status.render(agent.status, True, s_col)
            self.screen.blit(stat_surf, (240, row_y + 1))

            # Metrics
            exp_surf = self.font_table.render(f"{agent.total_expanded:6d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(exp_surf, (335, row_y))

            gen_surf = self.font_table.render(f"{agent.total_generated:6d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(gen_surf, (420, row_y))

            front_surf = self.font_table.render(f"{agent.last_frontier_size:3d} (max {agent.max_frontier_size})", True, COLOR_TEXT_WHITE)
            self.screen.blit(front_surf, (510, row_y))

            path_len = len(agent.path) if agent.path else agent.final_path_length
            path_surf = self.font_table.render(f"{path_len:3d}", True, COLOR_TEXT_WHITE)
            self.screen.blit(path_surf, (605, row_y))

            rep_surf = self.font_table.render(f"{agent.replans_count:2d}", True, (255, 120, 120) if agent.replans_count > 0 else COLOR_TEXT_WHITE)
            self.screen.blit(rep_surf, (670, row_y))

            row_y += 19

        # Hotkey legend at bottom
        legend_text = "HOTKEYS: [R] Reset Maze  [SPACE] Pause  [TAB] Search Overlay  [1-7] Focus Agent  [0] Show All  [+/-] Speed  [ESC] Quit"
        leg_surf = self.font_sub.render(legend_text, True, (100, 105, 125))
        self.screen.blit(leg_surf, (16, SCREEN_HEIGHT - 20))

    def draw_leaderboard(self, agents: List[Agent]):
        """
        High Score Leaderboard Overlay Modal.
        Triggered after all agents pass/finish.
        Displays rankings sorted by finish time, showing Time, Space (Peak Frontier),
        and Iterations (Expanded / Generated nodes).
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 215))  # Dark transparent backdrop
        self.screen.blit(overlay, (0, 0))

        dialog_w, dialog_h = 580, 360
        dx = (SCREEN_WIDTH - dialog_w) // 2
        dy = (SCREEN_HEIGHT - dialog_h) // 2
        dialog_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        # Dialog background and gold glow border
        pygame.draw.rect(self.screen, (20, 22, 30), dialog_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, width=2, border_radius=12)

        # Header Title
        title_surf = self.font_win_title.render("HIGH SCORE LEADERBOARD", True, (255, 215, 0))
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, dy + 28)))

        sub_surf = self.font_win_sub.render("ALL ALGORITHMS REACHED THE EXIT WITH ALL 3 KEYS", True, (180, 190, 210))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, dy + 54)))

        # Inner Table Box
        table_box = pygame.Rect(dx + 16, dy + 75, dialog_w - 32, 235)
        pygame.draw.rect(self.screen, (13, 15, 20), table_box, border_radius=8)
        pygame.draw.rect(self.screen, (40, 44, 58), table_box, width=1, border_radius=8)

        # Sort agents by finish_time
        sorted_agents = sorted(agents, key=lambda a: (a.finish_time if a.finish_time is not None else float('inf')))

        # Table Column Headers
        col_x = {
            "rank": dx + 26,
            "algo": dx + 75,
            "time": dx + 175,
            "iterations": dx + 265,
            "space": dx + 380,
            "path": dx + 485
        }

        h_y = dy + 85
        hdr_rank = self.font_table_hdr.render("RANK", True, COLOR_TEXT_MUTED)
        hdr_algo = self.font_table_hdr.render("ALGORITHM", True, COLOR_TEXT_MUTED)
        hdr_time = self.font_table_hdr.render("TIME", True, COLOR_TEXT_MUTED)
        hdr_iter = self.font_table_hdr.render("EXPANDED / GEN", True, COLOR_TEXT_MUTED)
        hdr_space = self.font_table_hdr.render("SPACE (FRONTIER)", True, COLOR_TEXT_MUTED)
        hdr_path = self.font_table_hdr.render("PATH LEN", True, COLOR_TEXT_MUTED)

        self.screen.blit(hdr_rank, (col_x["rank"], h_y))
        self.screen.blit(hdr_algo, (col_x["algo"], h_y))
        self.screen.blit(hdr_time, (col_x["time"], h_y))
        self.screen.blit(hdr_iter, (col_x["iterations"], h_y))
        self.screen.blit(hdr_space, (col_x["space"], h_y))
        self.screen.blit(hdr_path, (col_x["path"], h_y))

        pygame.draw.line(self.screen, (40, 44, 58), (dx + 20, h_y + 18), (dx + dialog_w - 20, h_y + 18), 1)

        # Render Leaderboard Rows
        row_y = h_y + 24
        medal_colors = {
            1: (255, 215, 0),   # 1st: Gold
            2: (200, 205, 215), # 2nd: Silver
            3: (205, 127, 50)   # 3rd: Bronze
        }

        for rank, agent in enumerate(sorted_agents, 1):
            rank_col = medal_colors.get(rank, COLOR_TEXT_MUTED)
            
            # Highlight top 1 row background
            if rank == 1:
                top_rect = pygame.Rect(dx + 20, row_y - 2, dialog_w - 40, 20)
                pygame.draw.rect(self.screen, (30, 34, 48), top_rect, border_radius=4)

            # Rank
            r_text = f"#{rank}"
            r_surf = self.font_rank.render(r_text, True, rank_col)
            self.screen.blit(r_surf, (col_x["rank"], row_y))

            # Algorithm Name
            algo_surf = self.font_table_hdr.render(agent.name, True, agent.color)
            self.screen.blit(algo_surf, (col_x["algo"], row_y))

            # Time
            time_str = self.format_time(agent.finish_time)
            time_surf = self.font_table.render(time_str, True, (255, 255, 255) if rank == 1 else COLOR_TEXT_WHITE)
            self.screen.blit(time_surf, (col_x["time"], row_y + 1))

            # Iterations (Expanded / Generated)
            iter_str = f"{agent.total_expanded} / {agent.total_generated}"
            iter_surf = self.font_table.render(iter_str, True, COLOR_TEXT_WHITE)
            self.screen.blit(iter_surf, (col_x["iterations"], row_y + 1))

            # Space taken (Peak Frontier nodes)
            space_str = f"{agent.max_frontier_size} states"
            space_surf = self.font_table.render(space_str, True, COLOR_TEXT_WHITE)
            self.screen.blit(space_surf, (col_x["space"], row_y + 1))

            # Path length
            path_str = f"{agent.final_path_length} steps"
            path_surf = self.font_table.render(path_str, True, COLOR_TEXT_WHITE)
            self.screen.blit(path_surf, (col_x["path"], row_y + 1))

            row_y += 24

        # Footer Instruction
        footer_text = self.font_sub.render("Press [R] to Generate a New Race  |  [ESC] to Quit", True, (130, 140, 165))
        self.screen.blit(footer_text, footer_text.get_rect(center=(SCREEN_WIDTH // 2, dy + dialog_h - 22)))

