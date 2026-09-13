"""
Helper heuristic functions for maze navigation with multi-keys and exit.
"""
from state import State

def manhattan_dist(p1, p2) -> int:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def calculate_heuristic(state: State, world) -> int:
    """
    Admissible heuristic for multi-key maze:
    1. Distance to closest remaining uncollected key.
    2. Estimated distance from keys to exit.
    """
    remaining_keys = [k for k in world.keys if k not in state.keys]
    
    if not remaining_keys:
        # All keys collected: just distance to exit
        return manhattan_dist(state.pos, world.exit_pos)
    
    # Distance to closest key
    dist_to_closest = min(manhattan_dist(state.pos, k) for k in remaining_keys)
    
    # Distance from remaining keys to exit
    key_to_exit = min(manhattan_dist(k, world.exit_pos) for k in remaining_keys)
    
    # Also factor spanning distance between remaining keys if > 1
    span_keys = 0
    if len(remaining_keys) > 1:
        span_keys = (len(remaining_keys) - 1) * 4
        
    return dist_to_closest + key_to_exit + span_keys
