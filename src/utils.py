FREE_LETTERS = set("RSTLNE")

def apply_free_letters(solution):
    """Reveal RSTLNE in the puzzle."""
    return [
        ch if ch == " " or ch in FREE_LETTERS else "_"
        for ch in solution
    ]

def apply_player_letters(solution, pattern, picks):
    """Reveal the player's chosen letters."""
    picks = set(picks.upper())
    new_pattern = []

    for sol_ch, existing in zip(solution, pattern):
        if sol_ch == " ":
            new_pattern.append(" ")
        elif existing != "_":
            new_pattern.append(existing)
        elif sol_ch in picks:
            new_pattern.append(sol_ch)
        else:
            new_pattern.append("_")

    return new_pattern

