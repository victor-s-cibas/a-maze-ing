import random
from collections import deque
from typing import List, Tuple, Optional, Set, Dict

class MazeGenerator:
    N, E, S, W = 1, 2, 4, 8
    OPPOSITE = {N: S, S: N, E: W, W: E}
    DX_DY = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}

    def __init__(self, width: int, height: int, perfect: bool = True):
        self.width = width
        self.height = height
        self.perfect = perfect
        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        self.pattern_cells: Set[Tuple[int, int]] = set()

    def generate(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                candidates = []
                if x < self.width - 1:
                    candidates.append((self.E, x + 1, y))
                if y < self.height - 1:
                    candidates.append((self.S, x, y + 1))
                
                if candidates:
                    direction, nx, ny = random.choice(candidates)
                    self.grid[y][x] &= ~direction
                    self.grid[ny][nx] &= ~self.OPPOSITE[direction]

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[str]:
        path = ""
        cx, cy = start
        ex, ey = end
        
        while cx < ex:
            path += "E"
            cx += 1
        while cx > ex:
            path += "W"
            cx -= 1
        while cy < ey:
            path += "S"
            cy += 1
        while cy > ey:
            path += "N"
            cy -= 1
            
        return path if path else None