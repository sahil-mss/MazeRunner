# 🏁 Classical Maze - Search Algorithm Race

A real-time, interactive 60 FPS AI visualizer where **7 classical search algorithms** race against each other through a dynamically generated labyrinth filled with alternating doors and key gates.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Framework](https://img.shields.io/badge/engine-pygame--ce-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

---

## 📖 Overview

In this benchmark simulation, 7 classic Artificial Intelligence search algorithms race in parallel to collect keys, navigate oscillating doors, and reach the exit in minimum time. 

The environment uses a non-blocking coroutine-like node expansion pipeline (`MAX_SEARCH_STEPS_PER_FRAME`) so that even exponential graph expansions (such as unguided BFS/DFS) run smoothly at a locked 60 frames per second with zero UI freezing.

### 🤖 The 7 Competing Algorithms

| # | Algorithm | Color | Type | Search Strategy & Characteristic |
|---|-----------|-------|------|----------------------------------|
| **1** | **DFS** (Depth-First Search) | 🔴 Red | Uninformed | Explores deepest paths first using a LIFO stack. Non-optimal; prone to long meandering paths. |
| **2** | **Heuristic Search** | 🟠 Orange | Informed | Pure Greedy-like evaluation prioritizing lower Manhattan distance to goals. |
| **3** | **A\* Search** | 🌸 Pink | Informed | Evaluates $f(n) = g(n) + h(n)$ (cost-so-far + admissible heuristic). Mathematically optimal path length. |
| **4** | **Greedy Best-First** | 🔷 Cyan | Informed | Prioritizes states closest to remaining keys/exit based solely on $h(n)$. Fast, but not necessarily shortest path. |
| **5** | **BFS** (Breadth-First Search) | 🟢 Green | Uninformed | Explores level by level using a FIFO queue. Guarantees the fewest steps in unweighted grids. |
| **6** | **IDS** (Iterative Deepening Search) | 🟣 Purple | Uninformed | Combines BFS-like optimality with DFS-like memory efficiency by incrementally expanding depth limits. |
| **7** | **UCS** (Uniform Cost Search) | 🟡 Yellow | Uninformed | Dijkstra’s variant on unit costs. Expands lowest path cost $g(n)$ nodes first. |

---

## 🎮 Game Rules & World Mechanics

1. **Maze Generation**: Generated via a randomized spanning tree maze algorithm with guaranteed solvability.
2. **Objective**:
   - Competing agents start at the blue entrance.
   - Agents must collect all diamond keys ($K$) scattered through the maze.
   - Once all keys are collected, the green exit ($E$) unlocks.
   - The first agent to reach the exit wins the race!
3. **Dynamic Alternating Doors**:
   - Doors are grouped into three distinct color channels: **Red**, **Blue**, and **Green**.
   - Every 3 seconds (`DOOR_TOGGLE_INTERVAL`), their state toggles: door 1 opens while door 2 closes (`[1, 0] -> [0, 1]`).
   - If an agent finds a door closed, it triggers a dynamic replan to discover alternate routes or wait for the door cycle.

---

## ⚡ Quick Setup & Installation

### Option 1: Automatic One-Click Setup (Recommended)

#### **On Windows:**
Double-click `setup.bat` or run in terminal:
```cmd
setup.bat
```

#### **On Linux / macOS:**
Make executable and run:
```bash
chmod +x setup.sh
./setup.sh
```

#### **Or Run Cross-Platform Python Setup Script:**
```bash
python setup.py
```
*`setup.py` automatically checks your Python version, configures a `.venv` virtual environment, installs dependencies from `requirements.txt`, and verifies the environment.*

---

### Option 2: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sahil-mss/MazeRunner.git
   cd MazeRunner
   ```

2. **Create and activate a virtual environment (recommended):**
   - **Windows:**
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the simulation:**
   ```bash
   python main.py
   ```

---

## ⌨️ Controls & Keybindings

During the race, you can interact with the visualizer using the following keys:

| Key | Action |
|-----|--------|
| <kbd>SPACE</kbd> | **Pause / Resume** simulation |
| <kbd>R</kbd> | **Reset** (generates a brand new maze and restarts the race) |
| <kbd>TAB</kbd> | **Toggle Search Overlays** (frontier dots, explored paths) |
| <kbd>+</kbd> / <kbd>=</kbd> | **Increase Agent Movement Speed** (up to 20 cells/s) |
| <kbd>-</kbd> | **Decrease Agent Movement Speed** (down to 1 cell/s) |
| <kbd>0</kbd> | **Focus: All Agents** (overlay all search frontiers) |
| <kbd>1</kbd> - <kbd>7</kbd> | **Focus: Specific Agent** (isolates search telemetry for a single algorithm) |
| <kbd>ESC</kbd> | **Exit** simulation |

---

## 📊 Telemetry & Live HUD

The user interface is divided into three distinct operational sections:

- **Top Bar**:
  - Live race stopwatch (minutes, seconds, centiseconds).
  - Status indicators (Racing, Paused, Leader detection).
  - Current move speed and active agent focus mode.
- **Center Canvas**:
  - Crisp, dark-mode maze rendering.
  - Multi-agent occupancy rendering (smooth radial offsets prevent overlapping icons).
  - Real-time frontier & explored state visualization colored to each algorithm.
- **Bottom Telemetry Panel**:
  - Real-time door cycle indicators (`[1, 0]` vs `[0, 1]`).
  - Table displaying for every algorithm: **Status**, **Nodes Expanded**, **Nodes Generated**, **Max Frontier**, **Replans**, **Keys Collected**, **Path Length**, and **Completion Time**.
- **Post-Race Leaderboard Overlay**:
  - Appears automatically once all algorithms finish, sorting agents by rank and time.

---

## 📁 Project Structure

```text
MazeRunner/
├── agent.py          # AI agent class: movement, state, search execution & telemetry
├── config.py         # Global settings: maze dimensions, speeds, colors, FPS
├── main.py           # Main loop, window initialization, and key event dispatcher
├── maze.py           # Procedural maze generator and wall/passage representations
├── renderer.py       # Pygame rendering engine (walls, doors, keys, paths, agents)
├── requirements.txt  # Python package dependencies (pygame-ce)
├── searches/         # Pluggable search algorithm implementations
│   ├── base_search.py   # Abstract base class with step-wise yield generator
│   ├── dfs.py           # Depth-First Search
│   ├── bfs.py           # Breadth-First Search
│   ├── astar.py         # A* Search (Manhattan distance heuristic)
│   ├── greedy.py        # Greedy Best-First Search
│   ├── heuristic.py     # Heuristic Search
│   ├── ids.py           # Iterative Deepening Search
│   └── ucs.py           # Uniform Cost Search (Dijkstra)
├── setup.bat         # Automated setup & run script for Windows
├── setup.py          # Cross-platform environment installer and verifier
├── setup.sh          # Automated setup & run script for macOS / Linux
├── state.py          # Search state tuple (row, col, collected_keys)
├── ui.py             # Top timer, telemetry tables, and leaderboard modals
└── world.py          # Game world state, door cycles, and collision validation
```

---

## 🛠️ Requirements & Compatibility

- **Python**: 3.8 or higher (tested on 3.8, 3.10, 3.12, and 3.14)
- **Library**: `pygame-ce` $\ge$ 2.5.0 (Community Edition of Pygame, offering superior performance and display scaling)
- **Supported Operating Systems**: Windows 10/11, macOS, and Linux (Ubuntu/Debian/Arch/Fedora)

---

## 🤝 Contributing & Customization

Want to add a custom search algorithm?
1. Create your algorithm in `searches/your_search.py` inheriting from `BaseSearch` in [`searches/base_search.py`](file:///d:/Projects/Pac%20Man/searches/base_search.py).
2. Implement the `search_step()` method returning generator steps.
3. Register your class in [`searches/__init__.py`](file:///d:/Projects/Pac%20Man/searches/__init__.py) and [`config.py`](file:///d:/Projects/Pac%20Man/config.py).
