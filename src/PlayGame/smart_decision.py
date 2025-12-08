"""
Smart Decision Function for Wheel of Fortune
Decides whether to spin the wheel or buy a vowel based on game state analysis.
"""

import re
import random
from typing import Tuple, Dict, List
from pattern_analyzer import WordPatternAnalyzer


def should_spin_or_buy_vowel(
    showing: str,
    winnings: int,
    previous_guesses: List[str],
    next_letter_candidate: str = None
) -> Tuple[str, str, str]:
    """
    Intelligent decision function for Wheel of Fortune gameplay.
    
    Args:
        showing: Current state of the puzzle with blanks as underscores
        winnings: Current player winnings
        previous_guesses: List of letters already guessed
        next_letter_candidate: The letter we're considering guessing (optional)
    
    Returns:
        Tuple of (decision, reasoning, best_consonant) where decision is 'spin', 'buy_vowel', or 'solve',
        reasoning explains the decision logic, and best_consonant is always provided as backup
    """
    
    # Get multiple consonant suggestions for enhanced reasoning
    consonant_suggestions = get_multiple_consonant_suggestions(showing, previous_guesses, 3)
    best_consonant = consonant_suggestions[0][0] if consonant_suggestions else get_best_consonant_guess(showing, previous_guesses)
    
    # Format consonant suggestions for reasoning
    consonant_info = ""
    if len(consonant_suggestions) >= 2:
        top_suggestions = [f"{c} ({explanation})" for c, _, explanation in consonant_suggestions[:2]]
        consonant_info = f"Top consonants: {', '.join(top_suggestions)}"
    else:
        consonant_info = f"Best consonant: {best_consonant}"
    
    # Analyze current game state
    game_state = analyze_game_state(showing, previous_guesses)
    
    # If we can't afford a vowel, we must spin
    if winnings < 250:
        return 'spin', f"Insufficient funds to buy vowel ($250 required). {consonant_info}", best_consonant
    
    # If puzzle is nearly complete (>80% revealed), consider solving
    if game_state['completion_ratio'] > 0.8:
        return 'solve', f"Puzzle is {game_state['completion_ratio']:.1%} complete - time to solve. If spinning instead: {consonant_info}", best_consonant
    
    # Calculate expected values and risks
    spin_analysis = analyze_spin_risk()
    vowel_analysis = analyze_vowel_value(game_state, previous_guesses)
    
    # Decision logic based on multiple factors
    decision_score = calculate_decision_score(
        game_state, spin_analysis, vowel_analysis, winnings
    )
    
    if decision_score['buy_vowel'] > decision_score['spin']:
        best_vowel = get_best_vowel_guess(showing, previous_guesses)
        return 'buy_vowel', f"{decision_score['reasoning']}. If spinning instead: {consonant_info}", best_consonant
    else:
        return 'spin', f"{decision_score['reasoning']}. {consonant_info}", best_consonant


def analyze_game_state(showing: str, previous_guesses: List[str]) -> Dict:
    """Analyze the current state of the puzzle."""
    
    total_letters = len(re.sub(r'[^A-Z_]', '', showing))
    blank_count = showing.count('_')
    revealed_count = total_letters - blank_count
    
    # Count vowels and consonants in revealed letters
    revealed_letters = re.sub(r'[^A-Z]', '', showing.replace('_', ''))
    vowels_revealed = sum(1 for c in revealed_letters if c in 'AEIOU')
    consonants_revealed = len(revealed_letters) - vowels_revealed
    
    # Estimate remaining vowels and consonants
    # Based on English letter frequency: ~40% vowels, ~60% consonants
    estimated_total_vowels = max(1, int(total_letters * 0.4))
    estimated_total_consonants = total_letters - estimated_total_vowels
    
    estimated_remaining_vowels = max(0, estimated_total_vowels - vowels_revealed)
    estimated_remaining_consonants = max(0, estimated_total_consonants - consonants_revealed)
    
    return {
        'total_letters': total_letters,
        'blank_count': blank_count,
        'revealed_count': revealed_count,
        'completion_ratio': revealed_count / total_letters if total_letters > 0 else 0,
        'vowels_revealed': vowels_revealed,
        'consonants_revealed': consonants_revealed,
        'estimated_remaining_vowels': estimated_remaining_vowels,
        'estimated_remaining_consonants': estimated_remaining_consonants,
        'vowel_density': estimated_remaining_vowels / blank_count if blank_count > 0 else 0
    }


def analyze_spin_risk() -> Dict:
    """Analyze the risk and expected value of spinning the wheel."""
    
    # Wheel values from the game
    wheel_values = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                   500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
    
    positive_values = [v for v in wheel_values if v > 0]
    lose_turn_count = wheel_values.count(0)
    bankrupt_count = wheel_values.count(-1)
    
    total_segments = len(wheel_values)
    
    return {
        'expected_value': sum(positive_values) / total_segments,  # Expected gain per spin
        'lose_turn_probability': lose_turn_count / total_segments,
        'bankrupt_probability': bankrupt_count / total_segments,
        'success_probability': len(positive_values) / total_segments,
        'average_positive_value': sum(positive_values) / len(positive_values) if positive_values else 0
    }


def analyze_vowel_value(game_state: Dict, previous_guesses: List[str]) -> Dict:
    """Analyze the expected value of buying a vowel."""
    
    # Common vowel frequencies in English
    vowel_frequencies = {'A': 0.082, 'E': 0.127, 'I': 0.070, 'O': 0.075, 'U': 0.028}
    
    # Filter out already guessed vowels
    available_vowels = {v: f for v, f in vowel_frequencies.items() 
                       if v not in previous_guesses}
    
    if not available_vowels:
        return {'expected_letters': 0, 'probability_of_hit': 0}
    
    # Estimate probability that a vowel will appear
    vowel_density = game_state['vowel_density']
    
    # Most frequent available vowel
    best_vowel_freq = max(available_vowels.values()) if available_vowels else 0
    
    # Expected number of letters revealed by buying a vowel
    expected_letters = vowel_density * game_state['blank_count'] * best_vowel_freq * 2
    
    return {
        'expected_letters': expected_letters,
        'probability_of_hit': min(0.9, vowel_density * 2),  # Cap at 90%
        'available_vowels': len(available_vowels),
        'best_vowel_frequency': best_vowel_freq
    }


def calculate_decision_score(
    game_state: Dict, 
    spin_analysis: Dict, 
    vowel_analysis: Dict, 
    winnings: int
) -> Dict:
    """Calculate scores for each decision option."""
    
    # Base scores
    spin_score = 0
    buy_vowel_score = 0
    
    # Factor 1: Expected value
    # Spinning: expected wheel value * probability of success * estimated consonants
    # Account for bankruptcy risk by reducing expected value
    spin_expected = (spin_analysis['average_positive_value'] * 
                    spin_analysis['success_probability'] * 
                    min(3, game_state['estimated_remaining_consonants']))
    
    # Subtract expected loss from bankruptcy (current winnings * bankruptcy probability)
    bankruptcy_risk = winnings * spin_analysis['bankrupt_probability']
    spin_expected = max(0, spin_expected - bankruptcy_risk)
    
    # Buying vowel: fixed cost but guaranteed if vowels exist
    vowel_expected = vowel_analysis['expected_letters'] * 150  # Higher value per vowel
    
    spin_score += spin_expected * 0.3
    buy_vowel_score += vowel_expected * 0.3
    
    # Factor 2: Risk assessment
    # Penalize spinning if high risk of bankruptcy/lose turn
    risk_penalty = (spin_analysis['bankrupt_probability'] * 500 + 
                   spin_analysis['lose_turn_probability'] * 200)
    spin_score -= risk_penalty * 0.2
    
    # Factor 3: Game stage
    completion = game_state['completion_ratio']
    
    if completion < 0.3:  # Early game - vowels more valuable
        buy_vowel_score += 100
    elif completion > 0.6:  # Late game - spinning for points more valuable
        spin_score += 100
    
    # Factor 4: Vowel density
    if game_state['vowel_density'] > 0.4:  # High vowel density
        buy_vowel_score += 150
    elif game_state['vowel_density'] < 0.2:  # Low vowel density
        spin_score += 100
    
    # Factor 5: Financial situation
    if winnings > 1000:  # Comfortable - can afford risks
        spin_score += 50
    elif winnings < 500:  # Conservative - preserve money for vowels
        buy_vowel_score += 75
    
    # Generate reasoning
    if buy_vowel_score > spin_score:
        reasoning = f"Buy vowel: High vowel density ({game_state['vowel_density']:.2f}), " \
                   f"expected {vowel_analysis['expected_letters']:.1f} letters revealed"
    else:
        reasoning = f"Spin wheel: Expected value ${spin_expected:.0f}, " \
                   f"{spin_analysis['success_probability']:.1%} success rate"
    
    return {
        'spin': spin_score,
        'buy_vowel': buy_vowel_score,
        'reasoning': reasoning
    }


def get_best_vowel_guess(showing: str, previous_guesses: List[str]) -> str:
    """Determine the best vowel to guess based on common patterns."""
    
    vowel_frequencies = {'E': 0.127, 'A': 0.082, 'O': 0.075, 'I': 0.070, 'U': 0.028}
    
    # Filter available vowels
    available_vowels = {v: f for v, f in vowel_frequencies.items() 
                       if v not in previous_guesses}
    
    if not available_vowels:
        return 'E'  # Fallback
    
    # Return most frequent available vowel
    return max(available_vowels.keys(), key=lambda x: available_vowels[x])


def get_best_consonant_guess(showing: str, previous_guesses: List[str]) -> str:
    """Determine the best consonant to guess based on pattern analysis and word completion."""
    
    # Use pattern analyzer for intelligent suggestions
    pattern_analyzer = WordPatternAnalyzer()
    suggestions = pattern_analyzer.get_top_consonant_suggestions(showing, previous_guesses, num_suggestions=1)
    
    if suggestions:
        return suggestions[0][0]  # Return the top suggestion
    
    # Fallback to frequency-based approach if pattern analysis fails
    consonant_frequencies = {
        'T': 0.091, 'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060,
        'D': 0.043, 'L': 0.040, 'C': 0.028, 'M': 0.024, 'W': 0.024,
        'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.013,
        'V': 0.010, 'K': 0.008, 'J': 0.001, 'X': 0.001, 'Q': 0.001, 'Z': 0.001
    }
    
    available_consonants = {c: f for c, f in consonant_frequencies.items() 
                           if c not in previous_guesses}
    
    if not available_consonants:
        return 'T'  # Ultimate fallback
    
    return max(available_consonants.keys(), key=lambda x: available_consonants[x])


def get_multiple_consonant_suggestions(showing: str, previous_guesses: List[str], num_suggestions: int = 3) -> List[Tuple[str, float, str]]:
    """Get multiple consonant suggestions with explanations for enhanced AI reasoning."""
    
    pattern_analyzer = WordPatternAnalyzer()
    return pattern_analyzer.get_top_consonant_suggestions(showing, previous_guesses, num_suggestions)


# Example usage and testing
if __name__ == "__main__":
    # Test scenarios
    test_scenarios = [
        {
            'showing': 'T_E _U_C_ _RO__ _O_',
            'winnings': 800,
            'previous_guesses': ['T', 'E', 'C', 'O'],
            'description': 'Mid-game with some vowels revealed'
        },
        {
            'showing': '_ _ _ _ _',
            'winnings': 300,
            'previous_guesses': [],
            'description': 'Early game, fresh puzzle'
        },
        {
            'showing': 'TH_ QU_CK _RO_N _O_',
            'winnings': 1500,
            'previous_guesses': ['T', 'H', 'Q', 'U', 'C', 'K', 'R', 'O', 'N'],
            'description': 'Late game, nearly complete'
        }
    ]
    
    print("Smart Decision Function Test Results:")
    print("=" * 50)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nScenario {i}: {scenario['description']}")
        print(f"Puzzle: {scenario['showing']}")
        print(f"Winnings: ${scenario['winnings']}")
        print(f"Previous guesses: {scenario['previous_guesses']}")
        
        decision, reasoning, best_consonant = should_spin_or_buy_vowel(
            scenario['showing'],
            scenario['winnings'],
            scenario['previous_guesses']
        )
        
        print(f"Decision: {decision.upper()}")
        print(f"Reasoning: {reasoning}")
        print(f"Best consonant (always provided): {best_consonant}")
        
        if decision == 'buy_vowel':
            best_vowel = get_best_vowel_guess(scenario['showing'], scenario['previous_guesses'])
            print(f"Recommended vowel: {best_vowel}")