"""
Smart Computer Player for Wheel of Fortune
Uses the smart decision function to make optimal choices.
"""

from smart_decision import should_spin_or_buy_vowel, get_best_vowel_guess, get_best_consonant_guess


def computer_turn_smart(showing, winnings, previous_guesses, turn):
    """
    Smart computer player that uses advanced decision-making logic.
    
    Args:
        showing: Current puzzle state with blanks
        winnings: List of winnings for all players
        previous_guesses: List of already guessed letters
        turn: Current turn number
    
    Returns:
        Tuple of (guess, dollar_value)
    """
    
    player_winnings = winnings[turn % 3]
    
    # Use smart decision function
    decision, reasoning, best_consonant = should_spin_or_buy_vowel(
        showing, player_winnings, previous_guesses
    )
    
    print(f"Smart AI reasoning: {reasoning}")
    
    if decision == 'solve':
        # For now, we'll just continue with normal play
        # In a full implementation, this would trigger solve logic
        decision = 'spin'  # Fallback to spinning
    
    if decision == 'buy_vowel':
        # Buy the best vowel
        vowel = get_best_vowel_guess(showing, previous_guesses)
        print(f"Smart AI bought vowel: {vowel}")
        winnings[turn % 3] -= 250
        return vowel, 0
    
    else:  # decision == 'spin'
        # Spin the wheel and guess best consonant
        from play_random_puzzle import spin_wheel
        dollar = spin_wheel()
        
        if dollar == 0:
            print("Smart AI lost a turn")
            return "_", 0
        elif dollar == -1:
            print("Smart AI went bankrupt")
            winnings[turn % 3] = 0
            return "_", 0
        else:
            consonant = best_consonant  # Use the pre-calculated best consonant
            print(f"Smart AI guessed consonant: {consonant}")
            return consonant, dollar


def computer_turn_smart_conservative(showing, winnings, previous_guesses, turn):
    """
    Conservative version of smart player - more likely to buy vowels.
    """
    
    player_winnings = winnings[turn % 3]
    
    # Modify the decision by being more conservative
    decision, reasoning, best_consonant = should_spin_or_buy_vowel(
        showing, player_winnings, previous_guesses
    )
    
    # Conservative adjustment: if we have money and there might be vowels, buy them
    blank_count = showing.count('_')
    vowels_guessed = sum(1 for v in 'AEIOU' if v in previous_guesses)
    
    if (player_winnings >= 250 and blank_count > 3 and vowels_guessed < 3 and 
        decision == 'spin'):
        decision = 'buy_vowel'
        reasoning = "Conservative strategy: preserving money for vowels"
    
    print(f"Conservative AI reasoning: {reasoning}")
    
    if decision == 'buy_vowel':
        vowel = get_best_vowel_guess(showing, previous_guesses)
        print(f"Conservative AI bought vowel: {vowel}")
        winnings[turn % 3] -= 250
        return vowel, 0
    else:
        from play_random_puzzle import spin_wheel
        dollar = spin_wheel()
        
        if dollar == 0:
            print("Conservative AI lost a turn")
            return "_", 0
        elif dollar == -1:
            print("Conservative AI went bankrupt")
            winnings[turn % 3] = 0
            return "_", 0
        else:
            consonant = best_consonant  # Use the pre-calculated best consonant
            print(f"Conservative AI guessed consonant: {consonant}")
            return consonant, dollar


def computer_turn_smart_aggressive(showing, winnings, previous_guesses, turn):
    """
    Aggressive version of smart player - more likely to spin for higher rewards.
    """
    
    player_winnings = winnings[turn % 3]
    
    decision, reasoning, best_consonant = should_spin_or_buy_vowel(
        showing, player_winnings, previous_guesses
    )
    
    # Aggressive adjustment: prefer spinning unless vowels are very likely
    vowel_density = showing.count('_') / max(1, len(showing.replace(' ', '')))
    
    if decision == 'buy_vowel' and vowel_density < 0.5:
        decision = 'spin'
        reasoning = "Aggressive strategy: spinning for higher rewards"
    
    print(f"Aggressive AI reasoning: {reasoning}")
    
    if decision == 'buy_vowel':
        vowel = get_best_vowel_guess(showing, previous_guesses)
        print(f"Aggressive AI bought vowel: {vowel}")
        winnings[turn % 3] -= 250
        return vowel, 0
    else:
        from play_random_puzzle import spin_wheel
        dollar = spin_wheel()
        
        if dollar == 0:
            print("Aggressive AI lost a turn")
            return "_", 0
        elif dollar == -1:
            print("Aggressive AI went bankrupt")
            winnings[turn % 3] = 0
            return "_", 0
        else:
            consonant = best_consonant  # Use the pre-calculated best consonant
            print(f"Aggressive AI guessed consonant: {consonant}")
            return consonant, dollar


# Test the smart players
if __name__ == "__main__":
    # Test scenario
    showing = "T_E _U_C_ _RO__ _O_"
    winnings = [800, 600, 400]
    previous_guesses = ['T', 'E', 'C', 'O']
    turn = 0
    
    print("Testing Smart Players:")
    print("=" * 30)
    print(f"Puzzle: {showing}")
    print(f"Winnings: {winnings}")
    print(f"Previous guesses: {previous_guesses}")
    print()
    
    # Test each player type
    players = [
        ("Smart", computer_turn_smart),
        ("Conservative", computer_turn_smart_conservative),
        ("Aggressive", computer_turn_smart_aggressive)
    ]
    
    for name, player_func in players:
        print(f"{name} Player:")
        # Make a copy of winnings to avoid modifying original
        test_winnings = winnings.copy()
        try:
            guess, dollar = player_func(showing, test_winnings, previous_guesses, turn)
            print(f"Result: guess='{guess}', dollar={dollar}")
            print(f"Updated winnings: {test_winnings}")
        except Exception as e:
            print(f"Error: {e}")
        print()