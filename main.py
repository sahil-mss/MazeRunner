"""
Main Entry Point.
Classical Maze - Search Algorithm Race.
Never blocks or freezes: 60 FPS rendering with incremental search expansions.
"""
import sys
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, ROWS, COLS,
    DEFAULT_MOVE_SPEED, MIN_MOVE_SPEED, MAX_MOVE_SPEED,
    AGENT_CONFIGS, COLOR_BG
)
from maze import Maze
from world import World
from agent import Agent
from renderer import Renderer
from ui import UI
from searches import (
    DFSSearch, BFSSearch, AStarSearch,
    GreedySearch, HeuristicSearch, IDSSearch, UCSSearch
)

def build_agents(world: World):
    search_classes = [
        DFSSearch,
        HeuristicSearch,
        AStarSearch,
        GreedySearch,
        BFSSearch,
        IDSSearch,
        UCSSearch
    ]
    agents = []
    for cfg, s_cls in zip(AGENT_CONFIGS, search_classes):
        agents.append(Agent(cfg["name"], cfg["color"], s_cls, world))
    return agents

def main():
    pygame.init()
    pygame.display.set_caption("Classical Maze - Search Algorithm Race")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    renderer = Renderer(screen)
    ui = UI(screen)

    # State variables
    maze = Maze(ROWS, COLS)
    world = World(maze)
    agents = build_agents(world)

    elapsed_time = 0.0
    paused = False
    winner = None
    move_speed = DEFAULT_MOVE_SPEED
    show_search = True
    focus_idx = 0  # 0: all, 1-7: specific agent

    def reset_race():
        nonlocal maze, world, agents, elapsed_time, winner, paused
        maze = Maze(ROWS, COLS)
        world = World(maze)
        agents = build_agents(world)
        elapsed_time = 0.0
        winner = None
        paused = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds elapsed in frame

        # ----------------------------------------------------
        # 1. Event Handling
        # ----------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_r:
                    reset_race()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_TAB:
                    show_search = not show_search
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    move_speed = min(MAX_MOVE_SPEED, move_speed + 1.0)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    move_speed = max(MIN_MOVE_SPEED, move_speed - 1.0)
                elif pygame.K_0 <= event.key <= pygame.K_7:
                    focus_idx = event.key - pygame.K_0

        # ----------------------------------------------------
        # 2. Logic Update
        # ----------------------------------------------------
        if not paused and winner is None:
            elapsed_time += dt

            # Update all agents incrementally (search stepping + movement)
            for agent in agents:
                reached_win = agent.update(dt, move_speed)
                if reached_win and winner is None:
                    winner = agent

        # ----------------------------------------------------
        # 3. Drawing / Rendering (Smooth 60 FPS)
        # ----------------------------------------------------
        screen.fill(COLOR_BG)

        # Draw Search overlays (dots, frontier, path)
        if show_search:
            renderer.draw_search_visualization(agents, focus_idx)

        # Draw Classical Maze with thin white wall lines
        renderer.draw_maze_lines(world)

        # Draw Start and Exit positions
        renderer.draw_start_and_exit(world)

        # Draw Colored Gates / Doors
        renderer.draw_doors(world)

        # Draw 3 Diamond Keys
        renderer.draw_keys(world)

        # Draw 7 Competing Agents (with smooth offsets for multi-occupancy)
        renderer.draw_agents(agents, focus_idx)

        # Top Timer and Header Bar
        ui.draw_top_bar(elapsed_time, paused, winner, move_speed, focus_idx)

        # Bottom Live Statistics Panel
        ui.draw_bottom_panel(agents, world, focus_idx)

        # Winner Overlay Modal if a winner has been crowned
        if winner is not None:
            ui.draw_winner_overlay(winner, elapsed_time)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
