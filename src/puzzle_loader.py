import random
from pathlib import Path

class PuzzleLoader:
    def __init__(self, puzzle_file: str):
        self.puzzle_file = Path(puzzle_file)
        if not self.puzzle_file.exists():
            raise FileNotFoundError(f"Puzzle file not found: {puzzle_file}")

    def load_random_puzzle(self):
        lines = [
            line.strip().upper()
            for line in self.puzzle_file.read_text().splitlines()
            if line.strip()
        ]
        return random.choice(lines)

