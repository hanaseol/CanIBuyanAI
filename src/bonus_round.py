from .utils import apply_free_letters, apply_player_letters

class BonusRoundGame:
    def __init__(self, solution: str):
        self.solution = solution.upper()
        self.pattern = apply_free_letters(self.solution)

    def get_pattern(self):
        return self.pattern

    def apply_player_letters(self, picks: str):
        self.pattern = apply_player_letters(self.solution, self.pattern, picks)

    def guess(self, guess: str) -> bool:
        return guess.upper() == self.solution

    def is_solved(self) -> bool:
        return "".join(self.pattern) == self.solution
