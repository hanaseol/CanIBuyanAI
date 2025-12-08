"""
Optimized AI Player for Wheel of Fortune
Uses the advanced AI optimizer for strategic decision making.
"""

from ai_optimizer import WheelOfFortuneOptimizer, GameState, format_recommendation_for_human


class OptimizedPlayer:
    """AI player that uses the advanced optimizer for decision making."""
    
    def __init__(self, personality='balanced'):
        """
        Initialize optimized player.
        
        Args:
            personality: 'balanced', 'aggressive', 'conservative'
        """
        self.optimizer = WheelOfFortuneOptimizer()
        self.personality = personality
        
        # Personality adjustments
        if personality == 'aggressive':
            self.risk_tolerance = 1.2  # More willing to take risks
            self.solve_threshold = 0.6  # Solve earlier
        elif personality == 'conservative':
            self.risk_tolerance = 0.8  # Less willing to take risks
            self.solve_threshold = 0.8  # Solve later
        else:  # balanced
            self.risk_tolerance = 1.0
            self.solve_threshold = 0.7
    
    def make_decision(self, showing, winnings, previous_guesses, turn):
        """
        Make an optimal decision using the AI optimizer.
        
        Args:
            showing: Current puzzle state with blanks
            winnings: List of winnings for all players
            previous_guesses: List of already guessed letters
            turn: Current turn number
        
        Returns:
            Tuple of (guess, dollar_value)
        """
        current_player = turn % 3
        
        # Create game state
        game_state = GameState(
            showing=showing,
            puzzle="",  # Unknown in real game
            winnings=winnings,
            previous_guesses=previous_guesses,
            current_player=current_player,
            turn_number=turn
        )
        
        # Get recommendation from optimizer
        recommendation = self.optimizer.get_optimal_recommendation(game_state)
        
        # Apply personality adjustments
        adjusted_action = self._apply_personality_adjustments(recommendation, game_state)
        
        # Print reasoning
        print(f"🤖 Optimized AI ({self.personality}) reasoning:")
        for reason in recommendation.reasoning[:3]:  # Show top 3 reasons
            print(f"  • {reason}")
        
        # Always show consonant suggestion if not already shown
        consonant_shown = any('consonant' in reason.lower() for reason in recommendation.reasoning[:3])
        if not consonant_shown and len(recommendation.reasoning) > 3:
            for reason in recommendation.reasoning[3:]:
                if 'consonant' in reason.lower():
                    print(f"  • {reason}")
                    break
        
        # Execute the decision
        return self._execute_decision(adjusted_action, recommendation, winnings, turn, previous_guesses)
    
    def _apply_personality_adjustments(self, recommendation, game_state):
        """Apply personality-based adjustments to the recommendation."""
        action = recommendation.action
        
        # Conservative adjustments
        if self.personality == 'conservative':
            # More likely to buy vowels if affordable
            if (action == 'spin' and game_state.player_winnings >= 500 and 
                len([v for v in 'AEIOU' if v not in game_state.previous_guesses]) > 0):
                if recommendation.confidence < 0.8:  # Not very confident in spinning
                    action = 'buy_vowel'
            
            # Less likely to solve unless very confident
            if action == 'solve' and recommendation.confidence < 0.7:
                action = 'spin'
        
        # Aggressive adjustments
        elif self.personality == 'aggressive':
            # More likely to spin for higher rewards
            if action == 'buy_vowel' and game_state.player_winnings > 1000:
                action = 'spin'
            
            # More likely to solve if trailing
            competitive_analysis = self.optimizer.analyze_competitive_position(game_state)
            if (competitive_analysis['relative_position'] == 'trailing' and 
                competitive_analysis['winnings_gap'] > 800):
                if action == 'buy_vowel':
                    action = 'solve'
        
        return action
    
    def _execute_decision(self, action, recommendation, winnings, turn, previous_guesses):
        """Execute the decided action."""
        current_player = turn % 3
        
        if action == 'buy_vowel':
            # Buy the recommended vowel, but double-check it's available
            vowel = recommendation.letter_suggestion
            
            if not vowel or vowel in previous_guesses:
                # Find first available vowel
                for v in ['E', 'A', 'O', 'I', 'U']:
                    if v not in previous_guesses:
                        vowel = v
                        break
                else:
                    # No vowels available, fall back to spinning
                    print("Optimized AI: No vowels available, spinning instead")
                    action = 'spin'
            
            if action == 'buy_vowel':
                print(f"Optimized AI bought vowel: {vowel}")
                winnings[current_player] -= 250
                return vowel, 0
        
        elif action == 'solve':
            # For now, we'll fall back to spinning since solve logic is complex
            # In a full implementation, this would trigger solve attempt
            print("Optimized AI wants to solve, but falling back to spin for now")
            action = 'spin'
        
        if action == 'spin':
            # Spin the wheel and guess best consonant
            from play_random_puzzle import spin_wheel
            dollar = spin_wheel()
            
            if dollar == 0:
                print("Optimized AI lost a turn")
                return "_", 0
            elif dollar == -1:
                print("Optimized AI went bankrupt")
                winnings[current_player] = 0
                return "_", 0
            else:
                # Get best available consonant
                consonant = recommendation.letter_suggestion
                if not consonant or consonant in previous_guesses:
                    # Find first available consonant
                    consonants = ['T', 'N', 'S', 'H', 'R', 'D', 'L', 'C', 'M', 'W', 'F', 'G', 'Y', 'P', 'B', 'V', 'K', 'J', 'X', 'Q', 'Z']
                    for c in consonants:
                        if c not in previous_guesses:
                            consonant = c
                            break
                    else:
                        consonant = 'T'  # Ultimate fallback
                
                print(f"Optimized AI guessed consonant: {consonant}")
                return consonant, dollar


def computer_turn_optimized(showing, winnings, previous_guesses, turn):
    """
    Optimized computer player function for integration with existing game.
    """
    player = OptimizedPlayer('balanced')
    return player.make_decision(showing, winnings, previous_guesses, turn)


def computer_turn_optimized_aggressive(showing, winnings, previous_guesses, turn):
    """
    Aggressive optimized computer player.
    """
    player = OptimizedPlayer('aggressive')
    return player.make_decision(showing, winnings, previous_guesses, turn)


def computer_turn_optimized_conservative(showing, winnings, previous_guesses, turn):
    """
    Conservative optimized computer player.
    """
    player = OptimizedPlayer('conservative')
    return player.make_decision(showing, winnings, previous_guesses, turn)


def get_human_suggestion(showing, winnings, previous_guesses, turn):
    """
    Get AI suggestion for human player without making the decision.
    
    Returns formatted suggestion string.
    """
    current_player = turn % 3
    
    # Create game state
    game_state = GameState(
        showing=showing,
        puzzle="",
        winnings=winnings,
        previous_guesses=previous_guesses,
        current_player=current_player,
        turn_number=turn
    )
    
    # Get recommendation
    optimizer = WheelOfFortuneOptimizer()
    recommendation = optimizer.get_optimal_recommendation(game_state)
    
    # Format for human display
    return format_recommendation_for_human(recommendation, detailed=True)


# Test the optimized players
if __name__ == "__main__":
    # Test scenario
    showing = "T_E _U_C_ _RO__ _O_"
    winnings = [800, 600, 400]
    previous_guesses = ['T', 'E', 'C', 'O']
    turn = 0
    
    print("Testing Optimized Players:")
    print("=" * 40)
    print(f"Puzzle: {showing}")
    print(f"Winnings: {winnings}")
    print(f"Previous guesses: {previous_guesses}")
    print()
    
    # Test each player type
    players = [
        ("Balanced", computer_turn_optimized),
        ("Aggressive", computer_turn_optimized_aggressive),
        ("Conservative", computer_turn_optimized_conservative)
    ]
    
    for name, player_func in players:
        print(f"{name} Optimized Player:")
        # Make a copy of winnings to avoid modifying original
        test_winnings = winnings.copy()
        try:
            guess, dollar = player_func(showing, test_winnings, previous_guesses, turn)
            print(f"Result: guess='{guess}', dollar={dollar}")
            print(f"Updated winnings: {test_winnings}")
        except Exception as e:
            print(f"Error: {e}")
        print()
    
    # Test human suggestion
    print("Human Player Suggestion:")
    print(get_human_suggestion(showing, winnings, previous_guesses, turn))