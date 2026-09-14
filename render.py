from typing import Dict, List, Set, Tuple

from mazegen import MazeGenerator

RESET: str = "\033[0m"
BOLD: str = "\033[1m"
EMPTY_BG: str = "\033[48;2;12;12;16m"
START_STYLE: str = "\033[1;38;2;0;255;220m\033[48;2;0;60;50m"
END_STYLE: str = "\033[1;38;2;255;50;150m\033[48;2;70;10;35m"
PATTERN_BG: str = "\033[48;2;242;226;190m"
PIPE_CHARS: str = "·╶╴─╷╭╮┬╵╰╯┴│├┤┼"

COLOR_PALETTE: List[Tuple[int, int, int]] = [
    (0, 255, 220),
    (50, 255, 80),
    (255, 220, 0),
    (255, 110, 20),
    (255, 50, 150),
]

THEMES: List[Tuple[str, str]] = [
    ("\033[38;2;255;30;60m", "\033[48;2;50;5;12m"),
    ("\033[38;2;0;230;255m", "\033[48;2;0;35;48m"),
    ("\033[38;2;255;40;180m", "\033[48;2;45;5;30m"),
    ("\033[38;2;50;255;100m", "\033[48;2;5;40;15m"),
    ("\033[38;2;180;90;255m", "\033[48;2;32;10;50m"),
]


def _build_path_coords(
    start: Tuple[int, int], path: str
) -> List[Tuple[int, int]]:
    """Expand path directions into ASCII grid coordinate list."""
    current_x, current_y = start
    start_y_coord = current_y * 2 + 1
    start_x_coord = current_x * 2 + 1
    coords: List[Tuple[int, int]] = [(start_y_coord, start_x_coord)]

    for step in path:
        if step == "N":
            coords.append((current_y * 2, current_x * 2 + 1))
            current_y -= 1
        elif step == "S":
            coords.append((current_y * 2 + 2, current_x * 2 + 1))
            current_y += 1
        elif step == "E":
            coords.append((current_y * 2 + 1, current_x * 2 + 2))
            current_x += 1
        elif step == "W":
            coords.append((current_y * 2 + 1, current_x * 2))
            current_x -= 1

        coords.append((current_y * 2 + 1, current_x * 2 + 1))

    return coords


def _get_gradient_ansi(step_index: int, total_steps: int) -> str:
    """Calculate ANSI background and foreground color gradient."""
    if total_steps <= 1:
        progress = 0.0
    else:
        progress = step_index / (total_steps - 1)

    scale = progress * (len(COLOR_PALETTE) - 1)
    palette_idx = min(int(scale), len(COLOR_PALETTE) - 2)
    blend_factor = scale - palette_idx

    r1, g1, b1 = COLOR_PALETTE[palette_idx]
    r2, g2, b2 = COLOR_PALETTE[palette_idx + 1]

    red = int(r1 + (r2 - r1) * blend_factor)
    green = int(g1 + (g2 - g1) * blend_factor)
    blue = int(b1 + (b2 - b1) * blend_factor)

    bg_red = int(red * 0.22)
    bg_green = int(green * 0.22)
    bg_blue = int(blue * 0.22)

    fg_ansi = f"\033[38;2;{red};{green};{blue}m"
    bg_ansi = f"\033[48;2;{bg_red};{bg_green};{bg_blue}m"

    return f"{fg_ansi}{bg_ansi}"


def get_path_map(
    start: Tuple[int, int], path: str
) -> Dict[Tuple[int, int], str]:
    """Map solution coordinates to their respective RGB color gradient."""
    if not path:
        return {}

    coords = _build_path_coords(start, path)
    total_steps = len(coords)

    path_dict: Dict[Tuple[int, int], str] = {}
    for index, cell in enumerate(coords):
        gradient = _get_gradient_ansi(index, total_steps)
        path_dict[cell] = gradient

    return path_dict


def _build_render_grid(generator: MazeGenerator) -> List[List[bool]]:
    """Construct boolean grid representing walls (True) and paths (False)."""
    grid_height = generator.height * 2 + 1
    grid_width = generator.width * 2 + 1

    render_grid: List[List[bool]] = []
    for _ in range(grid_height):
        row: List[bool] = []
        for _ in range(grid_width):
            row.append(True)
        render_grid.append(row)

    for y in range(generator.height):
        for x in range(generator.width):
            cell = generator.grid[y][x]
            render_y = y * 2 + 1
            render_x = x * 2 + 1

            render_grid[render_y][render_x] = False

            if not (cell & generator.E):
                render_grid[render_y][render_x + 1] = False
            if not (cell & generator.S):
                render_grid[render_y + 1][render_x] = False

    return render_grid


def _get_pattern_cells(generator: MazeGenerator) -> Set[Tuple[int, int]]:
    """Expand pattern cells into full grid coordinate set."""
    base_pattern: Set[Tuple[int, int]] = set()
    for pat_x, pat_y in generator.pattern_cells:
        cell_y = pat_y * 2 + 1
        cell_x = pat_x * 2 + 1
        base_pattern.add((cell_y, cell_x))

    pattern_cells: Set[Tuple[int, int]] = set(base_pattern)

    for y, x in base_pattern:
        if (y, x + 2) in base_pattern:
            pattern_cells.add((y, x + 1))
        if (y + 2, x) in base_pattern:
            pattern_cells.add((y + 1, x))

    return pattern_cells


def get_pipe_char(
    up: bool, down: bool, left: bool, right: bool
) -> Tuple[str, str]:
    """Return box drawing characters for wall connectivity."""
    index = 0
    if up:
        index += 8
    if down:
        index += 4
    if left:
        index += 2
    if right:
        index += 1

    if right:
        horizontal_fill = "─"
    else:
        horizontal_fill = " "

    return PIPE_CHARS[index], horizontal_fill


def _render_cell(
    pos: Tuple[int, int],
    start_pos: Tuple[int, int],
    end_pos: Tuple[int, int],
    render_grid: List[List[bool]],
    path_map: Dict[Tuple[int, int], str],
    pattern_cells: Set[Tuple[int, int]],
    theme: Tuple[str, str],
) -> str:
    """Render a single ASCII cell block according to its state."""
    pos_y, pos_x = pos
    grid_height = len(render_grid)
    grid_width = len(render_grid[0])
    wall_fg, wall_bg = theme

    if pos == start_pos:
        return f"{START_STYLE}\u2588\u2588{RESET}"

    if pos == end_pos:
        return f"{END_STYLE}\u2588\u2588{RESET}"

    if pos in path_map:
        has_up = pos_y > 0 and (pos_y - 1, pos_x) in path_map
        has_down = (
            pos_y < grid_height - 1 and (pos_y + 1, pos_x) in path_map
        )
        has_left = pos_x > 0 and (pos_y, pos_x - 1) in path_map
        has_right = (
            pos_x < grid_width - 1 and (pos_y, pos_x + 1) in path_map
        )

        char1, char2 = get_pipe_char(
            has_up, has_down, has_left, has_right
        )
        return f"{path_map[pos]}{BOLD}{char1}{char2}{RESET}"

    if render_grid[pos_y][pos_x]:
        has_up = pos_y > 0 and render_grid[pos_y - 1][pos_x]
        has_down = (
            pos_y < grid_height - 1 and render_grid[pos_y + 1][pos_x]
        )
        has_left = pos_x > 0 and render_grid[pos_y][pos_x - 1]
        has_right = (
            pos_x < grid_width - 1 and render_grid[pos_y][pos_x + 1]
        )

        char1, char2 = get_pipe_char(
            has_up, has_down, has_left, has_right
        )
        if pos in pattern_cells:
            cell_bg = PATTERN_BG
        else:
            cell_bg = wall_bg
        return f"{wall_fg}{cell_bg}{BOLD}{char1}{char2}{RESET}"

    if pos in pattern_cells:
        cell_bg = PATTERN_BG
    else:
        cell_bg = EMPTY_BG

    return f"{cell_bg}  {RESET}"


def render_ascii(
    generator: MazeGenerator,
    show_path: bool,
    path: str,
    start: Tuple[int, int],
    end: Tuple[int, int],
    theme: Tuple[str, str],
) -> None:
    """Render maze ASCII output to standard output."""
    if show_path and path:
        path_map = get_path_map(start, path)
    else:
        path_map = {}

    render_grid = _build_render_grid(generator)
    pattern_cells = _get_pattern_cells(generator)

    start_pos = (start[1] * 2 + 1, start[0] * 2 + 1)
    end_pos = (end[1] * 2 + 1, end[0] * 2 + 1)

    grid_height = len(render_grid)
    grid_width = len(render_grid[0])

    for y in range(grid_height):
        row_cells: List[str] = []
        for x in range(grid_width):
            cell_str = _render_cell(
                pos=(y, x),
                start_pos=start_pos,
                end_pos=end_pos,
                render_grid=render_grid,
                path_map=path_map,
                pattern_cells=pattern_cells,
                theme=theme,
            )
            row_cells.append(cell_str)
        print("".join(row_cells))
