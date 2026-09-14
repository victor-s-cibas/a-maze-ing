from collections import deque
import random
from typing import Deque, Dict, List, Optional, Set, Tuple

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

OPPOSITE: Dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

MOVE: Dict[int, Tuple[int, int]] = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST: (1, 0),
    WEST: (-1, 0),
}


class MazeGenerator:
    """Class responsible for generating the maze and solving it."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit_pos: Tuple[int, int] = exit_pos
        self.seed: Optional[int] = seed
        self.perfect: bool = perfect

        self._validate_inputs()

        if self.seed is not None:
            random.seed(self.seed)

        self.grid: List[List[int]] = []
        for _ in range(self.height):
            row: List[int] = []
            for _ in range(self.width):
                row.append(15)
            self.grid.append(row)

        self.solution_path: List[Tuple[int, int]] = []
        self.pattern_cells: Set[Tuple[int, int]] = set()
        self.E: int = EAST
        self.S: int = SOUTH

    def _validate_inputs(self) -> None:
        """Validate dimensions and coordinate bounds."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and Height must be positive integers.")

        ex, ey = self.entry
        sx, sy = self.exit_pos

        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ValueError("ENTRY coordinate is outside maze bounds.")

        if not (0 <= sx < self.width and 0 <= sy < self.height):
            raise ValueError("EXIT coordinate is outside maze bounds.")

        if self.entry == self.exit_pos:
            raise ValueError("ENTRY and EXIT coordinates must be different.")

    def get_grid(self) -> List[List[int]]:
        """Return the maze grid representation."""
        return self.grid

    def solve(self, entry: Tuple[int, int], exit_pos: Tuple[int, int]) -> str:
        """Find the shortest path using Breadth-First Search."""
        queue: Deque[Tuple[int, int]] = deque([entry])
        visited: Set[Tuple[int, int]] = {entry}
        came_from: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}

        directions: Dict[str, Tuple[Tuple[int, int], int]] = {
            "N": ((0, -1), NORTH),
            "S": ((0, 1), SOUTH),
            "E": ((1, 0), EAST),
            "W": ((-1, 0), WEST),
        }

        found: bool = False
        while queue:
            current = queue.popleft()
            if current == exit_pos:
                found = True
                break

            cx, cy = current
            for direction, info in directions.items():
                offset, bit = info
                dx, dy = offset
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    is_open = (self.grid[cy][cx] & bit) == 0
                    if is_open and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        came_from[(nx, ny)] = (current, direction)
                        queue.append((nx, ny))

        path_chars: List[str] = []
        if found:
            node = exit_pos
            while node != entry:
                prev, step_dir = came_from[node]
                path_chars.append(step_dir)
                node = prev
            path_chars.reverse()

        return "".join(path_chars)

    def get_solution(self) -> List[Tuple[int, int]]:
        """Return solution path coordinates."""
        return self.solution_path

    def _apply_pattern_42(self) -> None:
        """Apply closed cell '42' pattern mask at center of maze."""
        pattern: List[List[int]] = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        pat_h = len(pattern)
        pat_w = len(pattern[0])

        if self.width < pat_w + 2 or self.height < pat_h + 2:
            print("Warning: Maze too small to render '42' pattern.")
            return

        start_x = (self.width - pat_w) // 2
        start_y = (self.height - pat_h) // 2

        for r in range(pat_h):
            for c in range(pat_w):
                if pattern[r][c] == 1:
                    cell_x = start_x + c
                    cell_y = start_y + r
                    self.grid[cell_y][cell_x] = 15
                    self.pattern_cells.add((cell_x, cell_y))

    def generate(self) -> None:
        """Generate maze pathways using DFS backtracking."""
        if self.seed is not None:
            random.seed(self.seed)

        self._apply_pattern_42()

        stack: List[Tuple[int, int]] = [self.entry]
        visited: Set[Tuple[int, int]] = {self.entry}

        pat_h, pat_w = 5, 7
        if self.width >= pat_w + 2 and self.height >= pat_h + 2:
            start_x = (self.width - pat_w) // 2
            start_y = (self.height - pat_h) // 2
            pattern = [
                [1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ]
            for r in range(pat_h):
                for c in range(pat_w):
                    if pattern[r][c] == 1:
                        visited.add((start_x + c, start_y + r))

        while stack:
            cx, cy = stack[-1]
            unvisited: List[Tuple[int, Tuple[int, int]]] = []

            for direction, offset in MOVE.items():
                dx, dy = offset
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        unvisited.append((direction, (nx, ny)))

            if unvisited:
                direction, (nx, ny) = random.choice(unvisited)
                self.grid[cy][cx] &= ~direction
                self.grid[ny][nx] &= ~OPPOSITE[direction]

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
