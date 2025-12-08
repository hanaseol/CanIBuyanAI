class Display:
    @staticmethod
    def show_header():
        print("\n===== WHEEL OF FORTUNE — BONUS ROUND =====\n")

    @staticmethod
    def show_pattern(pattern):
        print("\nPuzzle:")
        print(" ".join(pattern))
        print()

    @staticmethod
    def msg(text):
        print(text)

