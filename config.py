"""
Global configuration settings, colors, dimensions, and game constants.
"""

# Maze Dimensions (classical odd dimensions for wall grid)
ROWS = 17
COLS = 23
TILE_SIZE = 28  # pixels per cell

# Window layout
MAZE_WIDTH = COLS * TILE_SIZE
MAZE_HEIGHT = ROWS * TILE_SIZE
TOP_BAR_HEIGHT = 80
BOTTOM_PANEL_HEIGHT = 200

SCREEN_WIDTH = MAZE_WIDTH
SCREEN_HEIGHT = TOP_BAR_HEIGHT + MAZE_HEIGHT + BOTTOM_PANEL_HEIGHT

# Performance & Timing
FPS = 60
DEFAULT_MOVE_SPEED = 5.0  # cells per second (adjustable with +/-)
MIN_MOVE_SPEED = 1.0
MAX_MOVE_SPEED = 20.0

# Search node expansions allowed per agent per frame (keeps UI at 60 FPS!)
MAX_SEARCH_STEPS_PER_FRAME = 35

# Color Palette (Dark Theme, High Contrast, Polished)
COLOR_BG = (12, 12, 16)
COLOR_PANEL_BG = (18, 18, 24)
COLOR_PANEL_BORDER = (45, 45, 60)
COLOR_WALL = (220, 225, 235)  # Thin classical maze wall line
COLOR_FLOOR = (12, 12, 16)

# UI Accent Colors
COLOR_TEXT_WHITE = (240, 245, 250)
COLOR_TEXT_MUTED = (140, 145, 165)
COLOR_TEXT_HEADER = (180, 195, 220)
COLOR_TIMER_ACCENT = (70, 200, 250)

# Goal and Key Colors
COLOR_KEY = (255, 215, 0)       # Gold
COLOR_EXIT = (50, 255, 140)      # Neon Emerald Green
COLOR_START = (100, 180, 255)    # Ice Blue

# Door Colors (Bright, distinct)
DOOR_COLORS = {
    "RED": (255, 60, 60),
    "BLUE": (60, 130, 255),
    "GREEN": (40, 220, 90)
}

# Agent Colors & Names
AGENT_CONFIGS = [
    {"name": "DFS", "color": (255, 75, 75)},       # Red
    {"name": "Heuristic", "color": (255, 150, 40)}, # Orange
    {"name": "A*", "color": (255, 105, 180)},      # Pink
    {"name": "Greedy", "color": (40, 225, 255)},    # Cyan
    {"name": "BFS", "color": (50, 225, 110)},      # Green
    {"name": "IDS", "color": (190, 100, 255)},     # Purple
    {"name": "UCS", "color": (255, 235, 50)}       # Yellow
]
