import random
import subprocess
import sys
from typing import Dict, List
from mazegen import MazeGenerator
from parse import parse_config, parse_tuple
from render import THEMES, render_ascii

RESET = "\033[0m"
BOLD = "\033[1m"


def export_maze(
    generator: MazeGenerator, config: Dict[str, str], path: str
) -> None:
    """Export generated maze to target output file."""
    try:
        with open(config["OUTPUT_FILE"], "w", encoding="utf-8") as file_obj:
            for row in generator.grid:
                hex_chars: List[str] = []
                for cell in row:
                    hex_chars.append(f"{cell:x}")
                hex_row = "".join(hex_chars)
                file_obj.write(f"{hex_row}\n")

            entry_str = config["ENTRY"]
            exit_str = config["EXIT"]
            file_obj.write(f"\n{entry_str}\n{exit_str}\n{path}\n")
    except Exception as error:
        print(f"Error saving output file: {error}")


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

        entry = parse_tuple(config["ENTRY"])
        exit_pos = parse_tuple(config["EXIT"])
        is_perfect = config.get("PERFECT", "False").lower() == "true"

        if "SEED" in config:
            random.seed(int(config["SEED"]))

        generator = MazeGenerator(
            width=width,
            height=height,
            entry=entry,
            exit_pos=exit_pos,
            perfect=is_perfect,
        )
        generator.generate()
        solution = generator.solve(entry, exit_pos) or ""
        export_maze(generator, config, solution)

        show_path = False
        theme_idx = 1

        while True:
            subprocess.run("clear")
            render_ascii(
                generator=generator,
                show_path=show_path,
                path=solution,
                start=entry,
                end=exit_pos,
                theme=THEMES[theme_idx],
            )

            print(f"\n{BOLD}=== A-Maze-ing ==={RESET}")
            print(f"{BOLD}1. Re-generate a new maze{RESET}")
            print(f"{BOLD}2. Show / Hide the shortest path{RESET}")
            print(f"{BOLD}3. Rotate the wall colours{RESET}")
            print(f"{BOLD}4. Quit{RESET}")

            choice = input(f"\n{BOLD}Choice? (1-4): {RESET}")

            if choice == "1":
                random.seed()
                generator = MazeGenerator(
                    width=width,
                    height=height,
                    entry=entry,
                    exit_pos=exit_pos,
                    perfect=is_perfect,
                )
                generator.generate()
                solution = generator.solve(entry, exit_pos) or ""
                export_maze(generator, config, solution)

            elif choice == "2":
                show_path = not show_path

            elif choice == "3":
                theme_idx = (theme_idx + 1) % len(THEMES)

            elif choice == "4":
                break

    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
