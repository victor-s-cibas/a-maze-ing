"""
A-Maze-ing: A maze generation, solving and visualization tool.
"""

import os
import random
import sys
from typing import Dict, List, Set, Tuple

from mazegen import MazeGenerator


# --- ANSI Style Constants ---
RESET = "\033[0m"
BOLD = "\033[1m"
EMPTY_BG = "\033[48;2;12;12;16m"
START_STYLE = "\033[1;38;2;0;255;220m\033[48;2;0;60;50m"
END_STYLE = "\033[1;38;2;255;50;150m\033[48;2;70;10;35m"
PATTERN_BG = "\033[48;2;242;226;190m"

PIPE_CHARS = "·╶╴─╷╭╮┬╵╰╯┴│├┤┼"

COLOR_PALETTE: List[Tuple[int, int, int]] = [
    (0, 255, 220),
    (50, 255, 80),
    (255, 220, 0),
    (255, 110, 20),
    (255, 50, 150),
]

NEON_THEMES: List[Tuple[str, str]] = [
    ("\033[38;2;255;30;60m", "\033[48;2;50;5;12m"),
    ("\033[38;2;0;230;255m", "\033[48;2;0;35;48m"),
    ("\033[38;2;255;40;180m", "\033[48;2;45;5;30m"),
    ("\033[38;2;50;255;100m", "\033[48;2;5;40;15m"),
    ("\033[38;2;180;90;255m", "\033[48;2;32;10;50m"),
]


def parse_config(filename: str) -> Dict[str, str]:
    """Parse configuration file and validate mandatory keys."""
    config: Dict[str, str] = {}

    try:
        with open(filename, "r", encoding="utf-8") as file_obj:
            for line in file_obj:
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#"):
                    continue

                if "=" not in clean_line:
                    raise ValueError(f"Invalid format: {clean_line}")

                key, val = clean_line.split("=", 1)
                config[key.strip().upper()] = val.strip()

    except Exception as error:
        print(f"Error parsing configuration file: {error}")
        sys.exit(1)

    required_keys = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
    ]

    for key in required_keys:
        if key not in config:
            print(f"Error: Missing mandatory key '{key}' in config.")
            sys.exit(1)

    return config


def parse_tuple(val: str) -> Tuple[int, int]:
    """Parse a coordinate tuple from a string like 'X,Y'."""
    try:
        x_str, y_str = val.split(",")
        return int(x_str), int(y_str)
    except Exception as error:
        raise ValueError(f"Invalid coordinate format '{val}'.") from error


def export_maze(
    generator: MazeGenerator, config: Dict[str, str], path: str
) -> None:
    """Export the generated maze to the target output file."""
    try:
        with open(config["OUTPUT_FILE"], "w", encoding="utf-8") as file_obj:
            for row in generator.grid:
                hex_row = "".join(f"{cell:x}" for cell in row)
                file_obj.write(f"{hex_row}\n")

            entry_str = config["ENTRY"]
            exit_str = config["EXIT"]
            file_obj.write(f"\n{entry_str}\n{exit_str}\n{path}\n")
    except Exception as error:
        print(f"Error saving output file: {error}")


def _build_path_coords(
    start: Tuple[int, int], path: str
) -> List[Tuple[int, int]]:
    """Expand path directions into ASCII grid coordinate list."""
    current_x, current_y = start
    coords: List[Tuple[int, int]] = [(current_y * 2 + 1, current_x * 2 + 1)]

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

        # Add the center of the newly reached cell
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

    return {
        cell: _get_gradient_ansi(index, total_steps)
        for index, cell in enumerate(coords)
    }


def get_pipe_char(
    up: bool, down: bool, left: bool, right: bool
) -> Tuple[str, str]:
    """Return box drawing characters for wall connectivity."""
    # Use binary flags to build an index: Up(8) | Down(4) | Left(2) | Right(1)
    index = (
        (int(up) << 3)
        | (int(down) << 2)
        | (int(left) << 1)
        | int(right)
    )
    horizontal_fill = "─" if right else " "
    return PIPE_CHARS[index], horizontal_fill


def _build_render_grid(generator: MazeGenerator) -> List[List[bool]]:
    """Construct boolean grid representing walls (True) and paths (False)."""
    grid_height = generator.height * 2 + 1
    grid_width = generator.width * 2 + 1
    render_grid = [[True] * grid_width for _ in range(grid_height)]

    for y in range(generator.height):
        for x in range(generator.width):
            cell = generator.grid[y][x]
            render_y, render_x = y * 2 + 1, x * 2 + 1

            render_grid[render_y][render_x] = False

            if not (cell & generator.E):
                render_grid[render_y][render_x + 1] = False
            if not (cell & generator.S):
                render_grid[render_y + 1][render_x] = False

    return render_grid


def _get_pattern_cells(generator: MazeGenerator) -> Set[Tuple[int, int]]:
    """Expand pattern cells into full grid coordinate set."""
    base_pattern = {
        (pat_y * 2 + 1, pat_x * 2 + 1)
        for pat_x, pat_y in generator.pattern_cells
    }
    pattern_cells = set(base_pattern)

    for y, x in base_pattern:
        if (y, x + 2) in base_pattern:
            pattern_cells.add((y, x + 1))
        if (y + 2, x) in base_pattern:
            pattern_cells.add((y + 1, x))

    return pattern_cells


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
        has_down = pos_y < grid_height - 1 and (pos_y + 1, pos_x) in path_map
        has_left = pos_x > 0 and (pos_y, pos_x - 1) in path_map
        has_right = pos_x < grid_width - 1 and (pos_y, pos_x + 1) in path_map

        char1, char2 = get_pipe_char(has_up, has_down, has_left, has_right)
        return f"{path_map[pos]}{BOLD}{char1}{char2}{RESET}"

    if render_grid[pos_y][pos_x]:
        has_up = pos_y > 0 and render_grid[pos_y - 1][pos_x]
        has_down = pos_y < grid_height - 1 and render_grid[pos_y + 1][pos_x]
        has_left = pos_x > 0 and render_grid[pos_y][pos_x - 1]
        has_right = pos_x < grid_width - 1 and render_grid[pos_y][pos_x + 1]

        char1, char2 = get_pipe_char(has_up, has_down, has_left, has_right)
        cell_bg = PATTERN_BG if pos in pattern_cells else wall_bg
        return f"{wall_fg}{cell_bg}{BOLD}{char1}{char2}{RESET}"

    cell_bg = PATTERN_BG if pos in pattern_cells else EMPTY_BG
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
    path_map = get_path_map(start, path) if show_path and path else {}
    render_grid = _build_render_grid(generator)
    pattern_cells = _get_pattern_cells(generator)

    start_pos = (start[1] * 2 + 1, start[0] * 2 + 1)
    end_pos = (end[1] * 2 + 1, end[0] * 2 + 1)

    for y in range(len(render_grid)):
        row_cells = [
            _render_cell(
                pos=(y, x),
                start_pos=start_pos,
                end_pos=end_pos,
                render_grid=render_grid,
                path_map=path_map,
                pattern_cells=pattern_cells,
                theme=theme,
            )
            for x in range(len(render_grid[0]))
        ]
        print("".join(row_cells))


def main() -> None:
    """Main CLI loop and program execution."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])

        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")

        entry_coords = parse_tuple(config["ENTRY"])
        exit_coords = parse_tuple(config["EXIT"])
        is_perfect = config.get("PERFECT", "False").lower() == "true"

        if "SEED" in config:
            random.seed(int(config["SEED"]))

        generator = MazeGenerator(width, height, is_perfect)
        generator.generate()
        solution = generator.solve(entry_coords, exit_coords) or ""
        export_maze(generator, config, solution)

        show_path = False
        theme_idx = 1

        while True:
            os.system("clear" if os.name == "posix" else "cls")
            render_ascii(
                generator=generator,
                show_path=show_path,
                path=solution,
                start=entry_coords,
                end=exit_coords,
                theme=NEON_THEMES[theme_idx],
            )

            print(f"\n{BOLD}=== A-Maze-ing ==={RESET}")
            print(f"{BOLD}1. Re-generate a new maze{RESET}")
            print(f"{BOLD}2. Show / Hide the shortest path{RESET}")
            print(f"{BOLD}3. Rotate the wall colours{RESET}")
            print(f"{BOLD}4. Quit{RESET}")

            choice = input(f"\n{BOLD}Choice? (1-4): {RESET}")

            if choice == "1":
                random.seed()
                generator = MazeGenerator(width, height, is_perfect)
                generator.generate()
                solution = generator.solve(entry_coords, exit_coords) or ""
                export_maze(generator, config, solution)

            elif choice == "2":
                show_path = not show_path

            elif choice == "3":
                theme_idx = (theme_idx + 1) % len(NEON_THEMES)

            elif choice == "4":
                break

    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()