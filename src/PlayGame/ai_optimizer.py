"""
Advanced AI Optimizer for Wheel of Fortune
Provides comprehensive strategic suggestions considering all game factors.

This optimizer analyzes:
- Probability of wheel outcomes (bankruptcy, lose turn, specific values)
- Risk vs reward calculations
- Opponent positioning and competitive analysis
- Expected value calculations for all possible actions
- Optimal timing for solving puzzles
- Financial impact analysis
"""

import re
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pattern_analyzer import WordPatternAnalyzer


@dataclass
class GameState:
    """Represents the current state of the game."""
    showing: str
    puzzle: str  # Full puzzle (if known for analysis)
    winnings: List[int]  # Winnings for all players
    previous_guesses: List[str]
    current_player: int
    turn_number: int
    
    @property
    def player_winnings(self) -> int:
        """Current player's winnings."""
        return self.winnings[self.current_player]
    
    @property
    def opponent_winnings(self) -> List[int]:
        """Other players' winnings."""
        return [w for i, w in enumerate(self.winnings) if i != self.current_player]
    
    @property
    def max_opponent_winnings(self) -> int:
        """Highest opponent winnings."""
        return max(self.opponent_winnings) if self.opponent_winnings else 0


@dataclass
class WheelAnalysis:
    """Analysis of wheel spin probabilities and expected values."""
    expected_value: float
    bankruptcy_probability: float
    lose_turn_probability: float
    success_probability: float
    high_value_probability: float  # Probability of landing on >$700
    average_positive_value: float
    risk_score: float  # Combined risk metric


@dataclass
class LetterAnalysis:
    """Analysis of letter frequencies and probabilities."""
    vowel_probability: Dict[str, float]
    consonant_probability: Dict[str, float]
    expected_vowel_count: float
    expected_consonant_count: float
    best_vowel: str
    best_consonant: str


@dataclass
class ActionRecommendation:
    """Recommendation for player action with detailed reasoning."""
    action: str  # 'spin', 'buy_vowel', 'solve'
    confidence: float  # 0-1 confidence score
    expected_gain: float
    risk_level: str  # 'low', 'medium', 'high'
    reasoning: List[str]  # Detailed reasoning points
    letter_suggestion: Optional[str] = None
    alternative_actions: List[Dict] = None


class WheelOfFortuneOptimizer:
    """Advanced AI optimizer for Wheel of Fortune gameplay."""
    
    def __init__(self):
        # Standard wheel values (can be customized)
        self.wheel_values = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                           500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
        
        # English letter frequencies (fallback)
        self.vowel_frequencies = {'A': 0.082, 'E': 0.127, 'I': 0.070, 'O': 0.075, 'U': 0.028}
        self.consonant_frequencies = {
            'T': 0.091, 'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060,
            'D': 0.043, 'L': 0.040, 'C': 0.028, 'M': 0.024, 'W': 0.024,
            'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.013,
            'V': 0.010, 'K': 0.008, 'J': 0.001, 'X': 0.001, 'Q': 0.001, 'Z': 0.001
        }
        
        # Pattern analyzer for intelligent consonant suggestions
        self.pattern_analyzer = WordPatternAnalyzer()
        
        # Vowel cost
        self.vowel_cost = 250
        
        # Solve bonus (typical game show bonus for solving)
        self.solve_bonus = 1000
    
    def analyze_wheel_probabilities(self) -> WheelAnalysis:
        """Analyze wheel spin probabilities and expected values."""
        positive_values = [v for v in self.wheel_values if v > 0]
        lose_turn_count = self.wheel_values.count(0)
        bankrupt_count = self.wheel_values.count(-1)
        high_value_count = len([v for v in self.wheel_values if v > 700])
        
        total_segments = len(self.wheel_values)
        
        # Calculate proper expected value: sum of (value * probability) for all outcomes
        # For positive values: gain that amount per letter
        # For lose turn (0): gain nothing, lose turn
        # For bankrupt (-1): lose all current winnings
        expected_value = sum(positive_values) / total_segments  # Only positive outcomes contribute to expected gain
        
        bankruptcy_prob = bankrupt_count / total_segments
        lose_turn_prob = lose_turn_count / total_segments
        success_prob = len(positive_values) / total_segments
        high_value_prob = high_value_count / total_segments
        avg_positive = sum(positive_values) / len(positive_values) if positive_values else 0
        
        # Risk score: higher is riskier
        risk_score = (bankruptcy_prob * 2.0) + (lose_turn_prob * 1.0)
        
        return WheelAnalysis(
            expected_value=expected_value,
            bankruptcy_probability=bankruptcy_prob,
            lose_turn_probability=lose_turn_prob,
            success_probability=success_prob,
            high_value_probability=high_value_prob,
            average_positive_value=avg_positive,
            risk_score=risk_score
        )
    
    def analyze_letters(self, game_state: GameState) -> LetterAnalysis:
        """Analyze letter probabilities and recommendations."""
        # Filter available letters
        available_vowels = {v: f for v, f in self.vowel_frequencies.items() 
                           if v not in game_state.previous_guesses}
        available_consonants = {c: f for c, f in self.consonant_frequencies.items() 
                               if c not in game_state.previous_guesses}
        
        # Estimate remaining letters in puzzle
        total_letters = len(re.sub(r'[^A-Z_]', '', game_state.showing))
        blank_count = game_state.showing.count('_')
        
        # Estimate vowel/consonant distribution (roughly 40% vowels, 60% consonants)
        estimated_vowels = max(1, int(blank_count * 0.4))
        estimated_consonants = blank_count - estimated_vowels
        
        # Best letter recommendations using pattern analysis
        best_vowel = max(available_vowels.keys(), key=lambda x: available_vowels[x]) if available_vowels else None
        
        # Use pattern analyzer for intelligent consonant suggestion
        pattern_suggestions = self.pattern_analyzer.get_top_consonant_suggestions(
            game_state.showing, game_state.previous_guesses, num_suggestions=1
        )
        best_consonant = pattern_suggestions[0][0] if pattern_suggestions else None
        
        # Fallback to frequency-based if pattern analysis fails
        if not best_consonant and available_consonants:
            best_consonant = max(available_consonants.keys(), key=lambda x: available_consonants[x])
        
        return LetterAnalysis(
            vowel_probability=available_vowels,
            consonant_probability=available_consonants,
            expected_vowel_count=estimated_vowels,
            expected_consonant_count=estimated_consonants,
            best_vowel=best_vowel,
            best_consonant=best_consonant
        )
    
    def calculate_spin_expected_value(self, game_state: GameState, wheel_analysis: WheelAnalysis, 
                                    letter_analysis: LetterAnalysis) -> float:
        """Calculate expected value of spinning the wheel."""
        # Get the best consonant and its estimated frequency in the puzzle
        best_consonant = letter_analysis.best_consonant
        
        # If no consonants available, return very low value
        if not letter_analysis.consonant_probability:
            return -1000
        
        # Calculate probability-weighted expected letters for available consonants
        total_available_freq = sum(letter_analysis.consonant_probability.values())
        if total_available_freq == 0:
            return -1000
            
        # Normalize frequencies for available letters only
        normalized_freq = {letter: freq / total_available_freq 
                          for letter, freq in letter_analysis.consonant_probability.items()}
        
        # Estimate letters revealed based on best available consonant
        best_consonant_freq = normalized_freq.get(letter_analysis.best_consonant, 0.05)
        
        # More realistic estimate: base it on puzzle completion and available letters
        blank_count = game_state.showing.count('_')
        completion_ratio = 1 - (blank_count / max(1, len(re.sub(r'[^A-Z_]', '', game_state.showing))))
        
        # As puzzle gets more complete, fewer letters per guess expected
        base_letters_estimate = max(1, 3 - (completion_ratio * 2))
        estimated_occurrences = min(blank_count, base_letters_estimate * best_consonant_freq * 1.5)
        
        # Expected value calculation:
        # P(success) * average_wheel_value * estimated_letter_count - P(fail) * penalties
        success_gain = (wheel_analysis.success_probability * 
                       wheel_analysis.average_positive_value * 
                       estimated_occurrences)
        
        # Risk penalties
        bankruptcy_penalty = (wheel_analysis.bankruptcy_probability * 
                            game_state.player_winnings)  # Lose all current winnings
        
        lose_turn_penalty = (wheel_analysis.lose_turn_probability * 
                           wheel_analysis.average_positive_value * 0.5)  # Opportunity cost
        
        total_expected_value = success_gain - bankruptcy_penalty - lose_turn_penalty
        
        return max(0, total_expected_value)  # Don't return negative expected values
    
    def calculate_vowel_expected_value(self, game_state: GameState, letter_analysis: LetterAnalysis) -> float:
        """Calculate expected value of buying a vowel."""
        if game_state.player_winnings < self.vowel_cost:
            return -float('inf')  # Can't afford it
        
        # Check if any vowels are available
        if not letter_analysis.best_vowel or not letter_analysis.vowel_probability:
            return -float('inf')  # No vowels available
        
        # Normalize frequencies for available vowels only
        total_available_vowel_freq = sum(letter_analysis.vowel_probability.values())
        if total_available_vowel_freq == 0:
            return -float('inf')
            
        normalized_vowel_freq = {letter: freq / total_available_vowel_freq 
                                for letter, freq in letter_analysis.vowel_probability.items()}
        
        # Estimate probability that vowel appears in puzzle
        blank_count = game_state.showing.count('_')
        completion_ratio = 1 - (blank_count / max(1, len(re.sub(r'[^A-Z_]', '', game_state.showing))))
        
        # More realistic vowel density based on remaining blanks and completion
        vowel_density = letter_analysis.expected_vowel_count / max(1, blank_count)
        best_vowel_freq = normalized_vowel_freq.get(letter_analysis.best_vowel, 0.1)
        
        # Expected letters revealed - more conservative as puzzle progresses
        base_vowel_estimate = max(1, 2.5 - (completion_ratio * 1.5))
        expected_letters = min(blank_count, vowel_density * best_vowel_freq * base_vowel_estimate)
        
        # Value per letter revealed (helps with puzzle completion)
        letter_value = 150  # Arbitrary value for puzzle progress
        
        return (expected_letters * letter_value) - self.vowel_cost
    
    def calculate_solve_expected_value(self, game_state: GameState) -> float:
        """Calculate expected value of attempting to solve."""
        # Estimate completion percentage
        total_letters = len(re.sub(r'[^A-Z_]', '', game_state.showing))
        revealed_letters = total_letters - game_state.showing.count('_')
        completion_ratio = revealed_letters / total_letters if total_letters > 0 else 0
        
        # Probability of successful solve (heuristic based on completion)
        if completion_ratio > 0.8:
            solve_probability = 0.9
        elif completion_ratio > 0.6:
            solve_probability = 0.7
        elif completion_ratio > 0.4:
            solve_probability = 0.4
        else:
            solve_probability = 0.1
        
        # Expected value = current winnings + solve bonus, weighted by probability
        total_potential = game_state.player_winnings + self.solve_bonus
        return total_potential * solve_probability
    
    def analyze_competitive_position(self, game_state: GameState) -> Dict:
        """Analyze position relative to opponents."""
        player_winnings = game_state.player_winnings
        max_opponent = game_state.max_opponent_winnings
        avg_opponent = sum(game_state.opponent_winnings) / len(game_state.opponent_winnings) if game_state.opponent_winnings else 0
        
        # Calculate competitive metrics
        winnings_gap = max_opponent - player_winnings
        relative_position = "leading" if player_winnings > max_opponent else "trailing"
        urgency_factor = max(0, winnings_gap / 1000)  # Higher when further behind
        
        return {
            'relative_position': relative_position,
            'winnings_gap': winnings_gap,
            'urgency_factor': urgency_factor,
            'max_opponent': max_opponent,
            'avg_opponent': avg_opponent,
            'pressure_level': 'high' if winnings_gap > 1000 else 'medium' if winnings_gap > 500 else 'low'
        }
    
    def get_optimal_recommendation(self, game_state: GameState) -> ActionRecommendation:
        """Get the optimal action recommendation with detailed analysis."""
        wheel_analysis = self.analyze_wheel_probabilities()
        letter_analysis = self.analyze_letters(game_state)
        competitive_analysis = self.analyze_competitive_position(game_state)
        
        # Calculate expected values for each action
        spin_ev = self.calculate_spin_expected_value(game_state, wheel_analysis, letter_analysis)
        vowel_ev = self.calculate_vowel_expected_value(game_state, letter_analysis)
        solve_ev = self.calculate_solve_expected_value(game_state)
        
        # Determine best action
        actions = [
            ('spin', spin_ev),
            ('buy_vowel', vowel_ev),
            ('solve', solve_ev)
        ]
        
        # Sort by expected value
        actions.sort(key=lambda x: x[1], reverse=True)
        best_action, best_ev = actions[0]
        
        # Generate reasoning
        reasoning = []
        confidence = 0.7  # Base confidence
        risk_level = 'medium'
        letter_suggestion = None  # Initialize letter suggestion
        
        # Get multiple consonant suggestions for enhanced reasoning
        consonant_suggestions = self.pattern_analyzer.get_top_consonant_suggestions(
            game_state.showing, game_state.previous_guesses, num_suggestions=3
        )
        
        best_consonant_backup = consonant_suggestions[0][0] if consonant_suggestions else (letter_analysis.best_consonant or 'T')
        best_vowel_backup = letter_analysis.best_vowel or 'E'
        
        # Format consonant suggestions for reasoning
        if len(consonant_suggestions) >= 2:
            consonant_info = f"Top consonants: {consonant_suggestions[0][0]} ({consonant_suggestions[0][2]}), {consonant_suggestions[1][0]} ({consonant_suggestions[1][2]})"
        else:
            consonant_info = f"Best consonant: {best_consonant_backup}"
        
        # Action-specific analysis
        if best_action == 'spin':
            reasoning.append(f"Spinning has highest expected value: ${best_ev:.0f}")
            reasoning.append(f"Wheel success probability: {wheel_analysis.success_probability:.1%}")
            reasoning.append(f"Bankruptcy risk: {wheel_analysis.bankruptcy_probability:.1%}")
            reasoning.append(consonant_info)
            
            if wheel_analysis.risk_score > 0.3:
                risk_level = 'high'
                confidence -= 0.1
            elif wheel_analysis.risk_score < 0.15:
                risk_level = 'low'
                confidence += 0.1
                
            letter_suggestion = best_consonant_backup
            
        elif best_action == 'buy_vowel':
            reasoning.append(f"Buying vowel has highest expected value: ${best_ev:.0f}")
            reasoning.append(f"Estimated vowels remaining: {letter_analysis.expected_vowel_count:.1f}")
            reasoning.append(f"Best vowel to buy: {best_vowel_backup}")
            reasoning.append(f"Cost: ${self.vowel_cost}")
            reasoning.append(f"If spinning instead: {consonant_info}")
            
            risk_level = 'low'  # Buying vowels is low risk
            confidence += 0.1
            letter_suggestion = best_vowel_backup
            
        else:  # solve
            completion_ratio = (len(re.sub(r'[^A-Z_]', '', game_state.showing)) - game_state.showing.count('_')) / len(re.sub(r'[^A-Z_]', '', game_state.showing))
            reasoning.append(f"Solving has highest expected value: ${best_ev:.0f}")
            reasoning.append(f"Puzzle completion: {completion_ratio:.1%}")
            reasoning.append(f"Potential total winnings: ${game_state.player_winnings + self.solve_bonus}")
            reasoning.append(f"If spinning instead: {consonant_info}")
            
            if completion_ratio > 0.8:
                risk_level = 'low'
                confidence += 0.2
            elif completion_ratio > 0.6:
                risk_level = 'medium'
            else:
                risk_level = 'high'
                confidence -= 0.2
        
        # Competitive analysis adjustments
        if competitive_analysis['relative_position'] == 'trailing':
            if competitive_analysis['winnings_gap'] > 1000:
                reasoning.append(f"You're trailing by ${competitive_analysis['winnings_gap']} - consider higher risk/reward actions")
                if best_action == 'buy_vowel':
                    # Suggest more aggressive play when trailing significantly
                    confidence -= 0.1
            else:
                reasoning.append(f"Close competition - current gap: ${competitive_analysis['winnings_gap']}")
        else:
            reasoning.append("You're in the lead - consider preserving your advantage")
            if best_action == 'spin' and wheel_analysis.risk_score > 0.25:
                confidence -= 0.05  # Slightly more conservative when leading
        
        # Financial situation analysis
        if game_state.player_winnings < 500:
            reasoning.append("Low winnings - be cautious with high-risk moves")
            if best_action == 'spin' and wheel_analysis.bankruptcy_probability > 0.1:
                confidence -= 0.1
        elif game_state.player_winnings > 1500:
            reasoning.append("Strong financial position - can afford calculated risks")
            confidence += 0.05
        
        # Generate alternative recommendations
        alternatives = []
        for action, ev in actions[1:3]:  # Top 2 alternatives
            if ev > -float('inf'):
                alternatives.append({
                    'action': action,
                    'expected_value': ev,
                    'confidence': max(0.1, confidence - 0.2)
                })
        
        # Clamp confidence to reasonable range
        confidence = max(0.1, min(0.95, confidence))
        
        return ActionRecommendation(
            action=best_action,
            confidence=confidence,
            expected_gain=best_ev,
            risk_level=risk_level,
            reasoning=reasoning,
            letter_suggestion=letter_suggestion,
            alternative_actions=alternatives
        )
    
    def get_detailed_analysis(self, game_state: GameState) -> Dict:
        """Get comprehensive analysis of the current game state."""
        wheel_analysis = self.analyze_wheel_probabilities()
        letter_analysis = self.analyze_letters(game_state)
        competitive_analysis = self.analyze_competitive_position(game_state)
        recommendation = self.get_optimal_recommendation(game_state)
        
        return {
            'wheel_analysis': wheel_analysis,
            'letter_analysis': letter_analysis,
            'competitive_analysis': competitive_analysis,
            'recommendation': recommendation,
            'game_metrics': {
                'completion_ratio': (len(re.sub(r'[^A-Z_]', '', game_state.showing)) - game_state.showing.count('_')) / len(re.sub(r'[^A-Z_]', '', game_state.showing)),
                'blanks_remaining': game_state.showing.count('_'),
                'letters_guessed': len(game_state.previous_guesses),
                'vowels_available': len(letter_analysis.vowel_probability),
                'consonants_available': len(letter_analysis.consonant_probability)
            }
        }


def format_recommendation_for_human(recommendation: ActionRecommendation, detailed: bool = True) -> str:
    """Format recommendation in a human-readable way."""
    output = []
    
    # Main recommendation
    action_text = {
        'spin': '🎰 SPIN THE WHEEL',
        'buy_vowel': '💰 BUY A VOWEL',
        'solve': '🧩 SOLVE THE PUZZLE'
    }
    
    output.append(f"\n{'='*50}")
    output.append(f"🤖 AI RECOMMENDATION: {action_text[recommendation.action]}")
    output.append(f"{'='*50}")
    
    # Confidence and risk
    confidence_bar = '█' * int(recommendation.confidence * 10) + '░' * (10 - int(recommendation.confidence * 10))
    output.append(f"Confidence: [{confidence_bar}] {recommendation.confidence:.1%}")
    output.append(f"Risk Level: {recommendation.risk_level.upper()}")
    output.append(f"Expected Gain: ${recommendation.expected_gain:.0f}")
    
    if recommendation.letter_suggestion:
        output.append(f"Suggested Letter: {recommendation.letter_suggestion}")
    
    # Reasoning
    output.append(f"\n📊 ANALYSIS:")
    for i, reason in enumerate(recommendation.reasoning, 1):
        output.append(f"  {i}. {reason}")
    
    # Alternatives
    if recommendation.alternative_actions and detailed:
        output.append(f"\n🔄 ALTERNATIVES:")
        for alt in recommendation.alternative_actions:
            output.append(f"  • {alt['action'].replace('_', ' ').title()}: ${alt['expected_value']:.0f} expected value")
    
    output.append(f"{'='*50}\n")
    
    return '\n'.join(output)


# Example usage and testing
if __name__ == "__main__":
    # Test the optimizer with various scenarios
    optimizer = WheelOfFortuneOptimizer()
    
    test_scenarios = [
        {
            'name': 'Early Game - Fresh Puzzle',
            'showing': '_ _ _ _ _ _ _ _',
            'winnings': [300, 450, 200],
            'previous_guesses': [],
            'current_player': 0
        },
        {
            'name': 'Mid Game - Some Progress',
            'showing': 'T_E _U_C_ _RO__ _O_',
            'winnings': [800, 600, 400],
            'previous_guesses': ['T', 'E', 'C', 'O'],
            'current_player': 0
        },
        {
            'name': 'Late Game - Nearly Complete',
            'showing': 'TH_ QU_CK _RO_N _O_',
            'winnings': [1200, 1800, 900],
            'previous_guesses': ['T', 'H', 'Q', 'U', 'C', 'K', 'R', 'O', 'N'],
            'current_player': 0
        },
        {
            'name': 'Trailing Badly',
            'showing': '_A_E _O_E _O_E_',
            'winnings': [200, 1500, 1200],
            'previous_guesses': ['A', 'E', 'O'],
            'current_player': 0
        }
    ]
    
    print("🎰 WHEEL OF FORTUNE AI OPTIMIZER TEST RESULTS")
    print("=" * 60)
    
    for scenario in test_scenarios:
        print(f"\n🎯 SCENARIO: {scenario['name']}")
        print(f"Puzzle: {scenario['showing']}")
        print(f"Winnings: {scenario['winnings']}")
        print(f"Previous Guesses: {scenario['previous_guesses']}")
        
        game_state = GameState(
            showing=scenario['showing'],
            puzzle="",  # Unknown in real game
            winnings=scenario['winnings'],
            previous_guesses=scenario['previous_guesses'],
            current_player=scenario['current_player'],
            turn_number=len(scenario['previous_guesses'])
        )
        
        recommendation = optimizer.get_optimal_recommendation(game_state)
        print(format_recommendation_for_human(recommendation, detailed=False))