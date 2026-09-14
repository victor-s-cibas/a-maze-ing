import random

NORTH: int = 1  # 0001
EAST: int = 2   # 0010
SOUTH: int = 4  # 0100
WEST: int = 8   # 1000

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

MOVE: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST: (1, 0),
    WEST: (-1, 0),
}


class MazeGenerator:
    """Classe responsável por gerar o labirinto e calcular sua solução."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit_pos: tuple[int, int] = exit_pos
        self.seed: int | None = seed
        self.perfect: bool = perfect

        self._validate_inputs()

        if self.seed is not None:
            random.seed(self.seed)

        # Grade inicializada com todas as paredes fechadas (15 / 0xF)
        self.grid: list[list[int]] = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]
        self.solution_path: list[tuple[int, int]] = []
        self.pattern_cells: set[tuple[int, int]] = set()
        self.E = EAST
        self.S = SOUTH

    def _validate_inputs(self) -> None:
        """Valida se as dimensões e coordenadas são válidas."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width e Height devem ser inteiros positivos.")

        ex, ey = self.entry
        sx, sy = self.exit_pos
        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ValueError("ENTRY está fora dos limites do labirinto.")
        if not (0 <= sx < self.width and 0 <= sy < self.height):
            raise ValueError("EXIT está fora dos limites do labirinto.")
        if self.entry == self.exit_pos:
            raise ValueError("ENTRY e EXIT devem ser diferentes.")

    def get_grid(self) -> list[list[int]]:
        """Retorna a matriz do labirinto em inteiros (bitmask)."""
        return self.grid

    def solve(self, entry: tuple[int,int], exit_pos: tuple[int,int]) -> str:
        from collections import deque

        queue = deque ([entry])
        visited = {entry}
        came_from = {}

        directions = {"N": ((0, -1), NORTH), "S": ((0, 1), SOUTH), "E": ((1, 0), EAST), "W": ((-1, 0), WEST)}

        found = False
        while queue:
            current = queue.popleft()
            if current == exit_pos:
                found = True
                break

            cx, cy = current
            for direction, ((dx, dy), bit) in directions.items():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[cy][cx] & bit == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        came_from[(nx, ny)] = (current, direction)
                        queue.append((nx, ny))

        path = []
        if found:
            node = exit_pos
            while node != entry:
                prev, direction = came_from[node]
                path.append(direction)
                node = prev
            path.reverse()
        return "".join(path)

    def get_solution(self) -> list[tuple[int, int]]:
        """Retorna o caminho da solução como lista de coordenadas (x, y)."""
        return self.solution_path

    def _apply_pattern_42(self) -> None:
        """Aplica a máscara do número 42 com células fechadas no centro do labirinto."""
        # Matriz binária do padrão 42 (5 linhas x 7 colunas)
        pattern: list[list[int]] = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        pat_h = len(pattern)
        pat_w = len(pattern[0])

        # Se o mapa for menor do que o padrão + bordas, emite aviso e ignora
        if self.width < pat_w + 2 or self.height < pat_h + 2:
            print("Warning: Too small maze to design '42' pattern.")
            return

        start_x = (self.width - pat_w) // 2
        start_y = (self.height - pat_h) // 2

        for r in range(pat_h):
            for c in range(pat_w):
                if pattern[r][c] == 1:
                    # Trava a célula com valor 15 (todas as paredes fechadas)
                    self.grid[start_y + r][start_x + c] = 15
                    self.pattern_cells.add((start_x + c, start_y + r))

    def generate(self) -> None:
        """Gera a estrutura do labirinto usando o algoritmo DFS."""
        if self.seed is not None:
            random.seed(self.seed)

        self._apply_pattern_42()

        # Pilha para o DFS e conjunto de células já visitadas
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}

        # Marca células do "42" como visitadas para o gerador não passar por cima delas
        pat_h, pat_w = 5, 7
        if self.width >= pat_w + 2 and self.height >= pat_h + 2:
            start_x = (self.width - pat_w) // 2
            start_y = (self.height - pat_h) // 2
            pattern = [
                [1, 0, 1, 0, 1, 1, 1],
                [1, 0, 1, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ]
            for r in range(pat_h):
                for c in range(pat_w):
                    if pattern[r][c] == 1:
                        visited.add((start_x + c, start_y + r))

        while stack:
            cx, cy = stack[-1]
            unvisited_neighbors: list[tuple[int, tuple[int, int]]] = []

            for direction, (dx, dy) in MOVE.items():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        unvisited_neighbors.append((direction, (nx, ny)))

            if unvisited_neighbors:
                direction, (nx, ny) = random.choice(unvisited_neighbors)
                # Remove a parede entre a célula atual e o vizinho escolhido
                self.grid[cy][cx] &= ~direction
                self.grid[ny][nx] &= ~OPPOSITE[direction]

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
