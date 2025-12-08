"""
SolveTimingAI - Advanced Wheel of Fortune AI Player
Focuses on optimal solve timing decisions using entropy and probability analysis.

This AI player makes strategic decisions about:
1. When to solve the puzzle early vs continuing to play
2. Whether to spin the wheel or buy vowels
3. Risk assessment based on game state and opponent scores
"""

from typing import Tuple, List, Optional
from solve_decision import should_solve_now, estimate_entropy, estimate_solve_probability
from smart_decision import should_spin_or_buy_vowel, get_best_vowel_guess, get_best_consonant_guess


class SolveTimingAI:
    """
    Advanced AI player that specializes in optimal solve timing decisions.
    
    This AI extends the existing smart decision logic with sophisticated
    analysis of when to solve the puzzle early versus continuing to play.
    """
    
    def __init__(self, risk_tolerance: float = 0.5, solve_aggressiveness: float = 0.5):
        """
        Initialize the SolveTimingAI with configurable parameters.
        
        Args:
            risk_tolerance: How much risk to take (0.0 = very conservative, 1.0 = very aggressive)
            solve_aggressiveness: How eager to solve early (0.0 = wait longer, 1.0 = solve quickly)
        """
        self.risk_tolerance = max(0.0, min(1.0, risk_tolerance))
        self.solve_aggressiveness = max(0.0, min(1.0, solve_aggressiveness))
        self.name = f"SolveTimingAI(risk={risk_tolerance:.1f}, solve={solve_aggressiveness:.1f})"
    
    def make_turn_decision(
        self, 
        showing: str, 
        winnings: List[int], 
        previous_guesses: List[str], 
        turn: int,
        puzzle: str = None,
        category: str = None
    ) -> Tuple[str, int, Optional[str]]:
        """
        Make a complete turn decision: solve, spin, or buy vowel.
        
        Args:
            showing: Current puzzle state with blanks
            winnings: List of all player winnings
            previous_guesses: Letters already guessed
            turn: Current turn number
            puzzle: Complete puzzle (for solve attempts)
            category: Puzzle category
        
        Returns:
            Tuple of (action, dollar_value, solve_guess)
            - action: 'solve', 'spin', or 'buy_vowel'
            - dollar_value: wheel value if spinning, 0 otherwise
            - solve_guess: puzzle guess if solving, None otherwise
        """
        player_index = turn % len(winnings)
        player_winnings = winnings[player_index]
        
        # Step 1: Decide if we should solve now
        should_solve, solve_reasoning, solve_analysis = should_solve_now(
            showing, winnings, player_index, category, previous_guesses, turn
        )
        
        # Adjust solve decision based on AI personality
        solve_threshold_adjustment = (self.solve_aggressiveness - 0.5) * 0.2
        adjusted_solve_prob = solve_analysis['solve_probability'] + solve_threshold_adjustment
        
        print(f"SolveTimingAI Analysis:")
        print(f"  Entropy: {solve_analysis['entropy']:.3f}")
        print(f"  Base Solve Probability: {solve_analysis['solve_probability']:.1%}")
        print(f"  Adjusted Solve Probability: {adjusted_solve_prob:.1%}")
        print(f"  Expected Spin Value: ${solve_analysis['spin_expected_value']:.0f}")
        print(f"  Score vs Opponents: {solve_analysis['score_difference']:+d}")
        
        # Apply personality adjustment to solve decision
        if self.solve_aggressiveness > 0.7:  # Aggressive solver
            should_solve = adjusted_solve_prob >= 0.6
        elif self.solve_aggressiveness < 0.3:  # Conservative solver
            should_solve = adjusted_solve_prob >= 0.8
        else:  # Balanced
            should_solve = adjusted_solve_prob >= 0.7
        
        if should_solve:
            print(f"SolveTimingAI Decision: SOLVE - {solve_reasoning}")
            solve_guess = self._generate_solve_guess(showing, category, previous_guesses)
            return 'solve', 0, solve_guess
        
        # Step 2: If not solving, decide between spin and buy vowel
        spin_or_vowel_decision, reasoning, best_consonant = should_spin_or_buy_vowel(
            showing, player_winnings, previous_guesses
        )
        
        # Apply risk tolerance to spin/vowel decision
        if spin_or_vowel_decision == 'spin' and self.risk_tolerance < 0.3:
            # Very conservative - prefer vowels if we can afford them
            if player_winnings >= 250:
                vowels_left = len(set('AEIOU') - set(previous_guesses))
                if vowels_left > 0:
                    spin_or_vowel_decision = 'buy_vowel'
                    reasoning = "Conservative risk tolerance: preferring vowel over spin"
        
        elif spin_or_vowel_decision == 'buy_vowel' and self.risk_tolerance > 0.7:
            # Very aggressive - prefer spinning for higher rewards
            spin_or_vowel_decision = 'spin'
            reasoning = "Aggressive risk tolerance: preferring spin over vowel"
        
        print(f"SolveTimingAI Decision: {spin_or_vowel_decision.upper()} - {reasoning}")
        
        if spin_or_vowel_decision == 'buy_vowel':
            return 'buy_vowel', 0, None
        else:
            return 'spin', 0, None  # Dollar value will be set by game engine
    
    def _generate_solve_guess(
        self, 
        showing: str, 
        category: str = None, 
        previous_guesses: List[str] = None
    ) -> str:
        """
        Generate a solve guess by filling in the blanks intelligently.
        
        This is a simplified implementation - in a full version, this would
        use more sophisticated NLP and pattern matching.
        """
        if previous_guesses is None:
            previous_guesses = []
        
        # For now, use a simple approach: fill blanks with most likely letters
        guess = showing
        
        # Common letter frequencies for filling blanks
        common_letters = 'ETAOINSHRDLUCMFWYGPBVKJXQZ'
        
        for letter in common_letters:
            if letter not in previous_guesses and '_' in guess:
                # Simple heuristic: try the letter and see if it makes sense
                # In a full implementation, this would use language models
                guess = guess.replace('_', letter, 1)
        
        return guess
    
    def get_letter_guess(
        self, 
        showing: str, 
        previous_guesses: List[str], 
        is_vowel: bool = False
    ) -> str:
        """
        Get the best letter guess (vowel or consonant).
        
        Args:
            showing: Current puzzle state
            previous_guesses: Letters already guessed
            is_vowel: Whether to guess a vowel or consonant
        
        Returns:
            Best letter to guess
        """
        if is_vowel:
            return get_best_vowel_guess(showing, previous_guesses)
        else:
            return get_best_consonant_guess(showing, previous_guesses)


def computer_turn_solve_timing_ai(
    showing: str, 
    winnings: List[int], 
    previous_guesses: List[str], 
    turn: int,
    puzzle: str = None,
    category: str = None,
    ai_instance: SolveTimingAI = None
) -> Tuple[str, int]:
    """
    Computer turn function for SolveTimingAI that integrates with the existing game engine.
    
    This function adapts the SolveTimingAI to work with the existing game loop structure.
    
    Args:
        showing: Current puzzle state
        winnings: List of player winnings
        previous_guesses: Letters already guessed
        turn: Current turn number
        puzzle: Complete puzzle for solve validation
        category: Puzzle category
        ai_instance: SolveTimingAI instance (creates default if None)
    
    Returns:
        Tuple of (guess, dollar_value) compatible with existing game engine
        - For solve attempts: returns ('SOLVE:' + guess, 0)
        - For letter guesses: returns (letter, dollar_value)
        - For failed actions: returns ('_', 0)
    """
    if ai_instance is None:
        ai_instance = SolveTimingAI()
    
    try:
        result = ai_instance.make_turn_decision(
            showing, winnings, previous_guesses, turn, puzzle, category
        )
        action, dollar_value, solve_guess = result
        
        if action == 'solve':
            # Return solve attempt in a format the game engine can recognize
            return f'SOLVE:{solve_guess}', 0
        
        elif action == 'buy_vowel':
            vowel = ai_instance.get_letter_guess(showing, previous_guesses, is_vowel=True)
            print(f"SolveTimingAI bought vowel: {vowel}")
            winnings[turn % len(winnings)] -= 250
            return vowel, 0
        
        elif action == 'spin':
            # Import here to avoid circular imports
            from play_random_puzzle import spin_wheel
            dollar = spin_wheel()
            
            if dollar == 0:
                print("SolveTimingAI lost a turn")
                return "_", 0
            elif dollar == -1:
                print("SolveTimingAI went bankrupt")
                winnings[turn % len(winnings)] = 0
                return "_", 0
            else:
                consonant = ai_instance.get_letter_guess(showing, previous_guesses, is_vowel=False)
                print(f"SolveTimingAI guessed consonant: {consonant}")
                return consonant, dollar
        
        else:
            print(f"SolveTimingAI: Unknown action {action}")
            return "_", 0
    
    except Exception as e:
        print(f"SolveTimingAI error: {e}")
        return "_", 0


# Predefined AI variants with different personalities
def computer_turn_solve_timing_conservative(showing, winnings, previous_guesses, turn, puzzle=None, category=None):
    """Conservative SolveTimingAI - waits for high confidence before solving."""
    conservative_ai = SolveTimingAI(risk_tolerance=0.2, solve_aggressiveness=0.3)
    return computer_turn_solve_timing_ai(showing, winnings, previous_guesses, turn, puzzle, category, conservative_ai)


def computer_turn_solve_timing_aggressive(showing, winnings, previous_guesses, turn, puzzle=None, category=None):
    """Aggressive SolveTimingAI - solves early and takes risks."""
    aggressive_ai = SolveTimingAI(risk_tolerance=0.8, solve_aggressiveness=0.8)
    return computer_turn_solve_timing_ai(showing, winnings, previous_guesses, turn, puzzle, category, aggressive_ai)


def computer_turn_solve_timing_balanced(showing, winnings, previous_guesses, turn, puzzle=None, category=None):
    """Balanced SolveTimingAI - moderate risk and solve timing."""
    balanced_ai = SolveTimingAI(risk_tolerance=0.5, solve_aggressiveness=0.5)
    return computer_turn_solve_timing_ai(showing, winnings, previous_guesses, turn, puzzle, category, balanced_ai)


# Test the AI
if __name__ == "__main__":
    # Test scenarios
    test_scenarios = [
        {
            'showing': 'T_E _U_C_ _RO__ _O_',
            'winnings': [800, 600, 400],
            'previous_guesses': ['T', 'E', 'C', 'O'],
            'turn': 0,
            'puzzle': 'THE QUICK BROWN FOX',
            'category': 'PHRASE',
            'description': 'Mid-game scenario'
        },
        {
            'showing': 'TH_ QU_CK _RO_N _O_',
            'winnings': [1200, 800, 600],
            'previous_guesses': ['T', 'H', 'Q', 'U', 'C', 'K', 'R', 'O', 'N'],
            'turn': 0,
            'puzzle': 'THE QUICK BROWN FOX',
            'category': 'PHRASE',
            'description': 'Nearly complete puzzle'
        }
    ]
    
    print("SolveTimingAI Test Results:")
    print("=" * 50)
    
    # Test different AI personalities
    ai_variants = [
        ("Conservative", SolveTimingAI(risk_tolerance=0.2, solve_aggressiveness=0.3)),
        ("Balanced", SolveTimingAI(risk_tolerance=0.5, solve_aggressiveness=0.5)),
        ("Aggressive", SolveTimingAI(risk_tolerance=0.8, solve_aggressiveness=0.8))
    ]
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['description']}")
        print(f"Puzzle: '{scenario['showing']}'")
        print(f"Winnings: {scenario['winnings']}")
        print(f"Previous guesses: {scenario['previous_guesses']}")
        print()
        
        for variant_name, ai in ai_variants:
            print(f"{variant_name} SolveTimingAI:")
            try:
                action, dollar, solve_guess = ai.make_turn_decision(
                    scenario['showing'],
                    scenario['winnings'].copy(),  # Don't modify original
                    scenario['previous_guesses'],
                    scenario['turn'],
                    scenario['puzzle'],
                    scenario['category']
                )
                print(f"  Action: {action}")
                if solve_guess:
                    print(f"  Solve Guess: '{solve_guess}'")
                    print(f"  Correct: {solve_guess == scenario['puzzle']}")
                print()
            except Exception as e:
                print(f"  Error: {e}")
                print()