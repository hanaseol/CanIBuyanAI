from src.puzzle_loader import PuzzleLoader
from src.bonus_round import BonusRoundGame
from src.display import Display

def main():
    loader = PuzzleLoader("data/bonus_puzzles.txt")
    solution = loader.load_random_puzzle()

    game = BonusRoundGame(solution)
    Display.show_header()

    Display.msg("Revealing R S T L N E...")
    Display.show_pattern(game.get_pattern())

    picks = input("Enter 3 consonants + 1 vowel (e.g., BCDA): ").strip().upper()
    if len(picks) != 4:
        Display.msg("Invalid input — must be exactly 4 letters.")
        return

    game.apply_player_letters(picks)
    Display.show_pattern(game.get_pattern())

    guess = input("Enter your final guess: ")

    if game.guess(guess):
        Display.msg("\n🎉 Correct! You win! 🎉")
    else:
        Display.msg(f"\n❌ Nope! The answer was: {solution}")

if __name__ == "__main__":
    main()

