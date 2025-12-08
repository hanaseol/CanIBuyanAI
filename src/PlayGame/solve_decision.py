"""
Solve Decision Module for Wheel of Fortune AI
Implements advanced decision-making logic for when to solve the puzzle early.

This module provides functions to:
1. Estimate puzzle entropy (information still missing)
2. Calculate probability of successful solve
3. Compute expected value of continuing vs solving
4. Make optimal solve timing decisions
"""

import re
import math
import random
from typing import Dict, List, Tuple, Optional
from collections import Counter


def estimate_entropy(showing: str, category: str = None) -> float:
    """
    Estimate the information entropy of the puzzle based on missing letters.
    
    Higher entropy = more uncertainty/information missing
    Lower entropy = puzzle is more predictable/solvable
    
    Args:
        showing: Current puzzle state with blanks as underscores
        category: Puzzle category (optional, for context-specific analysis)
    
    Returns:
        Entropy value (0.0 = fully revealed, higher = more uncertain)
    """
    # Clean the puzzle string - remove spaces and punctuation
    clean_puzzle = re.sub(r'[^A-Z_]', '', showing.upper())
    
    if not clean_puzzle:
        return 0.0
    
    total_positions = len(clean_puzzle)
    blank_positions = clean_puzzle.count('_')
    revealed_positions = total_positions - blank_positions
    
    if blank_positions == 0:
        return 0.0  # Fully revealed
    
    if revealed_positions == 0:
        return math.log2(26)  # Maximum entropy (any letter possible)
    
    # Calculate positional entropy based on revealed patterns
    revealed_letters = clean_puzzle.replace('_', '')
    letter_frequencies = Counter(revealed_letters)
    
    # Estimate remaining letter distribution
    # Use English letter frequencies as baseline
    english_frequencies = {
        'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070, 'N': 0.067,
        'S': 0.063, 'H': 0.061, 'R': 0.060, 'D': 0.043, 'L': 0.040, 'C': 0.028,
        'U': 0.028, 'M': 0.024, 'W': 0.024, 'F': 0.022, 'G': 0.020, 'Y': 0.020,
        'P': 0.019, 'B': 0.013, 'V': 0.010, 'K': 0.008, 'J': 0.001, 'X': 0.001,
        'Q': 0.001, 'Z': 0.001
    }
    
    # Calculate entropy based on possible letters for blank positions
    # Consider context from surrounding letters
    context_entropy = 0.0
    words = showing.split()
    
    for word in words:
        word_entropy = _calculate_word_entropy(word, english_frequencies)
        context_entropy += word_entropy
    
    # Normalize by number of blank positions
    if blank_positions > 0:
        context_entropy /= blank_positions
    
    # Apply category-specific adjustments
    if category:
        context_entropy *= _get_category_entropy_modifier(category)
    
    return min(context_entropy, math.log2(26))  # Cap at maximum possible entropy


def _calculate_word_entropy(word: str, letter_frequencies: Dict[str, float]) -> float:
    """Calculate entropy for a single word with blanks."""
    if '_' not in word:
        return 0.0
    
    word_entropy = 0.0
    for i, char in enumerate(word):
        if char == '_':
            # Consider context from surrounding letters
            context_letters = []
            if i > 0 and word[i-1] != '_':
                context_letters.append(word[i-1])
            if i < len(word) - 1 and word[i+1] != '_':
                context_letters.append(word[i+1])
            
            # Estimate possible letters based on context
            possible_letters = _get_possible_letters_for_position(
                word, i, context_letters, letter_frequencies
            )
            
            if possible_letters:
                # Calculate entropy for this position
                total_prob = sum(possible_letters.values())
                if total_prob > 0:
                    position_entropy = 0.0
                    for letter, prob in possible_letters.items():
                        normalized_prob = prob / total_prob
                        if normalized_prob > 0:
                            position_entropy -= normalized_prob * math.log2(normalized_prob)
                    word_entropy += position_entropy
            else:
                word_entropy += math.log2(26)  # No context, maximum uncertainty
    
    return word_entropy


def _get_possible_letters_for_position(
    word: str, 
    position: int, 
    context_letters: List[str], 
    letter_frequencies: Dict[str, float]
) -> Dict[str, float]:
    """Estimate possible letters for a position based on context."""
    # Start with base English frequencies
    possible_letters = letter_frequencies.copy()
    
    # Apply context-based filtering
    if context_letters:
        # Simple bigram/trigram analysis
        # This is a simplified version - could be enhanced with actual bigram data
        for context_letter in context_letters:
            if context_letter in 'AEIOU':  # Vowel context
                # Slightly favor consonants after vowels
                for letter in possible_letters:
                    if letter not in 'AEIOU':
                        possible_letters[letter] *= 1.2
            else:  # Consonant context
                # Slightly favor vowels after consonants
                for letter in possible_letters:
                    if letter in 'AEIOU':
                        possible_letters[letter] *= 1.3
    
    return possible_letters


def _get_category_entropy_modifier(category: str) -> float:
    """Get entropy modifier based on puzzle category."""
    category_modifiers = {
        'PHRASE': 1.1,      # Phrases can be more predictable
        'PERSON': 0.9,      # Names can be less predictable
        'PLACE': 0.95,      # Places somewhat predictable
        'THING': 1.0,       # Neutral
        'EVENT': 1.05,      # Events somewhat predictable
        'OCCUPATION': 0.9,  # Jobs can be less predictable
        'FOOD & DRINK': 1.1, # Food names often predictable
        'LIVING THING': 1.0,
        'QUOTATION': 1.2,   # Quotes can be very predictable
    }
    return category_modifiers.get(category.upper(), 1.0)


def estimate_solve_probability(showing: str, category: str = None, previous_guesses: List[str] = None) -> float:
    """
    Estimate the probability that an AI can correctly solve the puzzle now.
    
    Args:
        showing: Current puzzle state with blanks
        category: Puzzle category for context
        previous_guesses: Letters already guessed (for pattern analysis)
    
    Returns:
        Probability of successful solve (0.0 to 1.0)
    """
    if previous_guesses is None:
        previous_guesses = []
    
    # Calculate completion ratio
    clean_puzzle = re.sub(r'[^A-Z_]', '', showing.upper())
    if not clean_puzzle:
        return 1.0
    
    total_letters = len(clean_puzzle)
    blank_count = clean_puzzle.count('_')
    completion_ratio = (total_letters - blank_count) / total_letters
    
    # Base probability increases with completion
    base_prob = completion_ratio ** 1.5  # Non-linear increase
    
    # Adjust based on word structure and patterns
    words = showing.split()
    word_solvability = []
    
    for word in words:
        if '_' not in word:
            word_solvability.append(1.0)  # Fully revealed
        else:
            word_prob = _estimate_word_solve_probability(word, category)
            word_solvability.append(word_prob)
    
    # Overall solvability is the product of individual word probabilities
    # (all words need to be solvable)
    if word_solvability:
        pattern_prob = 1.0
        for prob in word_solvability:
            pattern_prob *= prob
    else:
        pattern_prob = base_prob
    
    # Combine base probability with pattern analysis
    solve_probability = (base_prob * 0.6) + (pattern_prob * 0.4)
    
    # Apply category-specific adjustments
    if category:
        category_modifier = _get_category_solve_modifier(category)
        solve_probability *= category_modifier
    
    # Bonus for having guessed common letters
    common_letters = set('ETAOINSHRDLU')
    guessed_common = len(set(previous_guesses) & common_letters)
    if guessed_common > 6:  # Good letter coverage
        solve_probability *= 1.1
    
    return min(solve_probability, 0.95)  # Cap at 95% to account for uncertainty


def _estimate_word_solve_probability(word: str, category: str = None) -> float:
    """Estimate probability of solving a single word."""
    if '_' not in word:
        return 1.0
    
    word_length = len(word)
    blank_count = word.count('_')
    revealed_count = word_length - blank_count
    
    if revealed_count == 0:
        return 0.1  # Very hard to solve with no letters
    
    # Pattern recognition probability
    pattern_prob = revealed_count / word_length
    
    # Adjust based on word structure
    if word_length <= 3:
        pattern_prob *= 1.2  # Short words easier to guess
    elif word_length >= 8:
        pattern_prob *= 0.9  # Long words harder
    
    # Check for common patterns
    if re.search(r'_ING$', word):  # -ING ending
        pattern_prob *= 1.3
    elif re.search(r'^THE_', word):  # THE- beginning
        pattern_prob *= 1.4
    elif re.search(r'_ED$', word):  # -ED ending
        pattern_prob *= 1.2
    
    return min(pattern_prob, 0.9)


def _get_category_solve_modifier(category: str) -> float:
    """Get solve probability modifier based on category."""
    category_modifiers = {
        'PHRASE': 1.2,      # Common phrases easier to solve
        'PERSON': 0.8,      # Names harder without full info
        'PLACE': 0.9,       # Places moderately difficult
        'THING': 1.0,       # Neutral
        'EVENT': 1.1,       # Events often follow patterns
        'OCCUPATION': 0.85, # Jobs can be tricky
        'FOOD & DRINK': 1.15, # Food names often familiar
        'LIVING THING': 1.0,
        'QUOTATION': 1.3,   # Quotes very solvable with context
    }
    return category_modifiers.get(category.upper(), 1.0)


def expected_value_of_spinning(
    showing: str, 
    scores: List[int], 
    player_index: int,
    previous_guesses: List[str] = None
) -> float:
    """
    Calculate expected value of spinning the wheel vs solving now.
    
    Args:
        showing: Current puzzle state
        scores: List of all player scores
        player_index: Index of current player
        previous_guesses: Letters already guessed
    
    Returns:
        Expected value of spinning (can be negative if solving is better)
    """
    if previous_guesses is None:
        previous_guesses = []
    
    # Wheel analysis
    wheel_values = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1,
                   500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
    
    positive_values = [v for v in wheel_values if v > 0]
    lose_turn_prob = wheel_values.count(0) / len(wheel_values)
    bankrupt_prob = wheel_values.count(-1) / len(wheel_values)
    success_prob = len(positive_values) / len(wheel_values)
    avg_positive_value = sum(positive_values) / len(positive_values)
    
    # Estimate remaining consonants
    clean_puzzle = re.sub(r'[^A-Z_]', '', showing.upper())
    consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
    guessed_consonants = set(previous_guesses) & set(consonants)
    
    # Estimate how many consonants are likely in the remaining blanks
    blank_count = clean_puzzle.count('_')
    estimated_consonant_ratio = 0.6  # Roughly 60% of letters are consonants
    estimated_remaining_consonants = blank_count * estimated_consonant_ratio
    
    # Probability that our next consonant guess will hit
    remaining_consonants = set(consonants) - guessed_consonants
    if remaining_consonants:
        # Use frequency-based estimation
        consonant_frequencies = {
            'T': 0.091, 'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060,
            'D': 0.043, 'L': 0.040, 'C': 0.028, 'M': 0.024, 'W': 0.024,
            'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.013,
            'V': 0.010, 'K': 0.008, 'J': 0.001, 'X': 0.001, 'Q': 0.001, 'Z': 0.001
        }
        
        available_consonant_freq = sum(
            consonant_frequencies.get(c, 0.001) for c in remaining_consonants
        )
        consonant_hit_prob = min(0.8, available_consonant_freq * 10)  # Rough estimation
    else:
        consonant_hit_prob = 0.1  # Very low if no consonants left
    
    # Expected letters revealed per successful spin
    expected_letters_per_hit = min(3, estimated_remaining_consonants / max(1, len(remaining_consonants)))
    
    # Calculate expected value of spinning
    spin_expected_value = (
        success_prob * consonant_hit_prob * avg_positive_value * expected_letters_per_hit
        - bankrupt_prob * scores[player_index]  # Risk of losing current winnings
        - lose_turn_prob * 100  # Opportunity cost of losing turn
    )
    
    # Factor in competitive pressure
    current_score = scores[player_index]
    max_opponent_score = max(scores[:player_index] + scores[player_index+1:]) if len(scores) > 1 else 0
    
    if current_score < max_opponent_score:
        # Behind in score - spinning might be worth more risk
        spin_expected_value *= 1.2
    elif current_score > max_opponent_score + 500:
        # Ahead by a lot - more conservative
        spin_expected_value *= 0.8
    
    return spin_expected_value


def should_solve_now(
    showing: str, 
    scores: List[int], 
    player_index: int,
    category: str = None,
    previous_guesses: List[str] = None,
    turn_number: int = 0
) -> Tuple[bool, str, Dict[str, float]]:
    """
    Main decision function: should the AI solve the puzzle now?
    
    Args:
        showing: Current puzzle state
        scores: List of all player scores  
        player_index: Index of current player
        category: Puzzle category
        previous_guesses: Letters already guessed
        turn_number: Current turn number (for early round difficulty adjustment)
    
    Returns:
        Tuple of (should_solve, reasoning, analysis_data)
    """
    if previous_guesses is None:
        previous_guesses = []
    
    # Calculate key metrics
    entropy = estimate_entropy(showing, category)
    solve_prob = estimate_solve_probability(showing, category, previous_guesses)
    spin_expected_value = expected_value_of_spinning(showing, scores, player_index, previous_guesses)
    
    # Current game state
    current_score = scores[player_index]
    max_opponent_score = max(scores[:player_index] + scores[player_index+1:]) if len(scores) > 1 else 0
    
    # Calculate solve threshold based on multiple factors
    base_solve_threshold = 0.7  # Base probability threshold for solving
    
    # Adjust threshold based on game situation
    if current_score < max_opponent_score:
        # Behind - need to take more risks, lower threshold
        solve_threshold = base_solve_threshold - 0.1
    elif current_score > max_opponent_score + 1000:
        # Way ahead - be more conservative, higher threshold
        solve_threshold = base_solve_threshold + 0.1
    else:
        solve_threshold = base_solve_threshold
    
    # Adjust based on expected value of spinning
    if spin_expected_value < 100:
        # Low expected value from spinning - more likely to solve
        solve_threshold -= 0.1
    elif spin_expected_value > 500:
        # High expected value from spinning - less likely to solve
        solve_threshold += 0.1
    
    # Adjust based on entropy (information remaining)
    if entropy < 1.0:  # Low entropy - puzzle is quite clear
        solve_threshold -= 0.15
    elif entropy > 3.0:  # High entropy - still very uncertain
        solve_threshold += 0.1
    
    # Adjust based on turn number (early rounds are harder to solve)
    if turn_number <= 6:  # First 2 rounds (3 players * 2 turns each)
        # Early game - much harder to solve, increase threshold significantly
        early_round_penalty = 0.2 + (0.05 * (6 - turn_number))  # 0.2-0.5 penalty
        solve_threshold += early_round_penalty
    elif turn_number <= 12:  # Rounds 3-4
        # Mid-early game - still harder to solve
        solve_threshold += 0.1
    # Late game (turn_number > 12) - no penalty, normal solving
    
    # Make decision
    should_solve = solve_prob >= solve_threshold
    
    # Generate reasoning
    early_round_note = ""
    if turn_number <= 6:
        early_round_note = f" (Early round {turn_number//3 + 1} - higher threshold)"
    elif turn_number <= 12:
        early_round_note = f" (Mid-game round {turn_number//3 + 1} - moderate threshold)"
    
    if should_solve:
        reasoning = (f"SOLVE: {solve_prob:.1%} solve probability exceeds threshold "
                    f"({solve_threshold:.1%}){early_round_note}. Entropy: {entropy:.2f}, "
                    f"Expected spin value: ${spin_expected_value:.0f}")
    else:
        reasoning = (f"CONTINUE: {solve_prob:.1%} solve probability below threshold "
                    f"({solve_threshold:.1%}){early_round_note}. Expected spin value: ${spin_expected_value:.0f}")
    
    # Analysis data for debugging/tuning
    analysis_data = {
        'entropy': entropy,
        'solve_probability': solve_prob,
        'solve_threshold': solve_threshold,
        'spin_expected_value': spin_expected_value,
        'current_score': current_score,
        'max_opponent_score': max_opponent_score,
        'score_difference': current_score - max_opponent_score
    }
    
    return should_solve, reasoning, analysis_data


# Test and demonstration functions
if __name__ == "__main__":
    # Test scenarios
    test_scenarios = [
        {
            'showing': 'T_E _U_C_ _RO__ _O_',
            'scores': [800, 600, 400],
            'player_index': 0,
            'category': 'PHRASE',
            'previous_guesses': ['T', 'E', 'C', 'O'],
            'description': 'Mid-game scenario'
        },
        {
            'showing': 'TH_ QU_CK _RO_N _O_',
            'scores': [1200, 800, 600],
            'player_index': 0,
            'category': 'PHRASE',
            'previous_guesses': ['T', 'H', 'Q', 'U', 'C', 'K', 'R', 'O', 'N'],
            'description': 'Nearly complete puzzle'
        },
        {
            'showing': '_ _ _ _ _ _ _',
            'scores': [300, 200, 100],
            'player_index': 0,
            'category': 'PERSON',
            'previous_guesses': [],
            'description': 'Early game, no letters revealed'
        }
    ]
    
    print("Solve Decision Analysis Test Results:")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nScenario {i}: {scenario['description']}")
        print(f"Puzzle: '{scenario['showing']}'")
        print(f"Category: {scenario['category']}")
        print(f"Scores: {scenario['scores']} (Player {scenario['player_index']} turn)")
        print(f"Previous guesses: {scenario['previous_guesses']}")
        
        # Test individual functions
        entropy = estimate_entropy(scenario['showing'], scenario['category'])
        solve_prob = estimate_solve_probability(
            scenario['showing'], scenario['category'], scenario['previous_guesses']
        )
        spin_ev = expected_value_of_spinning(
            scenario['showing'], scenario['scores'], scenario['player_index'], 
            scenario['previous_guesses']
        )
        
        print(f"\nAnalysis:")
        print(f"  Entropy: {entropy:.3f}")
        print(f"  Solve Probability: {solve_prob:.1%}")
        print(f"  Expected Value of Spinning: ${spin_ev:.0f}")
        
        # Main decision
        should_solve, reasoning, analysis = should_solve_now(
            scenario['showing'], scenario['scores'], scenario['player_index'],
            scenario['category'], scenario['previous_guesses']
        )
        
        print(f"\nDecision: {'SOLVE NOW' if should_solve else 'CONTINUE PLAYING'}")
        print(f"Reasoning: {reasoning}")
        print("-" * 40)