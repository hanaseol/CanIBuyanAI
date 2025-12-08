"""
Solve Timing Experiments - Comprehensive AI Evaluation
Runs large-scale simulations to evaluate SolveTimingAI performance against other AI types.

This script:
1. Runs 10,000+ games between different AI types
2. Collects detailed statistics on win rates, earnings, and solve timing
3. Generates CSV reports and analysis summaries
4. Provides insights into optimal solve timing strategies
"""

import sys
import os
import csv
import random
import time
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import statistics

# Add the PlayGame directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'PlayGame'))

from play_random_puzzle import get_random_puzzle, is_vowel, is_consonant, print_board
from smart_player import computer_turn_smart, computer_turn_smart_conservative, computer_turn_smart_aggressive
from solve_timing_ai import (
    computer_turn_solve_timing_conservative, 
    computer_turn_solve_timing_aggressive, 
    computer_turn_solve_timing_balanced
)


class GameSimulator:
    """Simulates Wheel of Fortune games for AI evaluation."""
    
    def __init__(self):
        self.wheel_values = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1,
                            500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
        
        # Available AI types and their functions
        self.ai_functions = {
            'smart': computer_turn_smart,
            'conservative': computer_turn_smart_conservative,
            'aggressive': computer_turn_smart_aggressive,
            'solve_timing': computer_turn_solve_timing_balanced,
            'solve_conservative': computer_turn_solve_timing_conservative,
            'solve_aggressive': computer_turn_solve_timing_aggressive,
        }
    
    def spin_wheel(self) -> int:
        """Simulate spinning the wheel."""
        return random.choice(self.wheel_values)
    
    def simulate_game(self, player_types: List[str], max_turns: int = 200, verbose: bool = False) -> Dict[str, Any]:
        """
        Simulate a single game between AI players.
        
        Args:
            player_types: List of AI type names for each player
            max_turns: Maximum turns before declaring a draw
            verbose: Whether to print game progress
        
        Returns:
            Dictionary with game results and statistics
        """
        # Get random puzzle
        puzzle, clue, date, game_type = get_random_puzzle()
        if verbose:
            print(f"Puzzle: {puzzle}")
            print(f"Category: {game_type}")
            print(f"Clue: {clue}")
        
        # Initialize game state
        showing = puzzle
        import re
        showing = re.sub(r"[A-Z]", "_", showing)
        
        previous_guesses = []
        turn = 0
        winnings = [0, 0, 0]
        game_stats = {
            'turns_taken': 0,
            'letters_guessed': 0,
            'vowels_bought': 0,
            'bankruptcies': 0,
            'solve_attempts': 0,
            'winner': None,
            'final_winnings': [0, 0, 0],
            'puzzle': puzzle,
            'category': game_type,
            'player_types': player_types.copy()
        }
        
        # Game loop
        while showing != puzzle and turn < max_turns:
            player_index = turn % 3
            player_type = player_types[player_index]
            
            if verbose:
                print(f"\nTurn {turn + 1}: Player {player_index} ({player_type})")
                print(f"Current state: {showing}")
                print(f"Winnings: {winnings}")
            
            # Get AI decision
            try:
                if player_type in self.ai_functions:
                    ai_func = self.ai_functions[player_type]
                    # Check if this is a solve timing AI (takes 6 args) or traditional AI (takes 4 args)
                    if player_type.startswith('solve_'):
                        guess, dollar = ai_func(showing, winnings, previous_guesses, turn, puzzle, game_type)
                    else:
                        guess, dollar = ai_func(showing, winnings, previous_guesses, turn)
                else:
                    # Fallback to smart AI
                    guess, dollar = computer_turn_smart(showing, winnings, previous_guesses, turn)
                
                game_stats['turns_taken'] += 1
                
                # Handle solve attempts
                if guess.startswith('SOLVE:'):
                    solve_guess = guess[6:]
                    game_stats['solve_attempts'] += 1
                    
                    if verbose:
                        print(f"Player {player_index} attempts to solve: '{solve_guess}'")
                    
                    if solve_guess == puzzle:
                        game_stats['winner'] = player_index
                        game_stats['final_winnings'] = winnings.copy()
                        if verbose:
                            print(f"CORRECT! Player {player_index} wins!")
                        break
                    else:
                        if verbose:
                            print("Wrong solution, next player")
                        turn += 1
                        continue
                
                # Handle letter guesses
                if guess in previous_guesses and guess != "_":
                    if verbose:
                        print("Already guessed, next player")
                    turn += 1
                    continue
                
                previous_guesses.append(guess)
                
                if guess == "_":  # Lost turn or bankrupt
                    if dollar == -1:
                        game_stats['bankruptcies'] += 1
                        winnings[player_index] = 0
                    turn += 1
                    continue
                
                # Count letter types
                if is_vowel(guess):
                    game_stats['vowels_bought'] += 1
                else:
                    game_stats['letters_guessed'] += 1
                
                # Update puzzle state
                correct_places = []
                for pos, char in enumerate(puzzle):
                    if char == guess:
                        correct_places.append(pos)
                
                if len(correct_places) > 0:
                    # Correct guess - add winnings and update showing
                    winnings[player_index] += dollar * len(correct_places)
                    for correct_letter in correct_places:
                        showing = showing[:correct_letter] + guess + showing[correct_letter + 1:]
                    
                    if verbose:
                        print(f"Correct! Found {len(correct_places)} instances")
                else:
                    # Wrong guess
                    if verbose:
                        print("Not in puzzle, next player")
                    turn += 1
                
            except Exception as e:
                if verbose:
                    print(f"Error with {player_type}: {e}")
                turn += 1
        
        # Game ended - determine winner if not already set
        if game_stats['winner'] is None:
            if showing == puzzle:
                # Puzzle completed by letters - highest score wins
                max_winnings = max(winnings)
                game_stats['winner'] = winnings.index(max_winnings)
            else:
                # Max turns reached - draw or highest score wins
                max_winnings = max(winnings)
                if max_winnings > 0:
                    game_stats['winner'] = winnings.index(max_winnings)
                else:
                    game_stats['winner'] = -1  # Draw
        
        game_stats['final_winnings'] = winnings.copy()
        
        return game_stats
    
    def run_tournament(
        self, 
        player_combinations: List[List[str]], 
        games_per_combination: int = 1000,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run a tournament between different AI combinations.
        
        Args:
            player_combinations: List of player type combinations to test
            games_per_combination: Number of games to run for each combination
            verbose: Whether to print progress
        
        Returns:
            Tournament results and statistics
        """
        results = {
            'combinations': {},
            'overall_stats': defaultdict(lambda: defaultdict(int)),
            'ai_performance': defaultdict(lambda: {
                'games_played': 0,
                'wins': 0,
                'total_winnings': 0,
                'solve_attempts': 0,
                'successful_solves': 0
            })
        }
        
        total_games = len(player_combinations) * games_per_combination
        games_completed = 0
        
        for combination in player_combinations:
            combo_key = '-vs-'.join(combination)
            results['combinations'][combo_key] = {
                'games_played': 0,
                'wins_by_player': [0, 0, 0],
                'total_winnings': [0, 0, 0],
                'avg_winnings': [0, 0, 0],
                'solve_attempts': 0,
                'successful_solves': 0,
                'avg_turns': 0,
                'bankruptcies': 0
            }
            
            combo_stats = results['combinations'][combo_key]
            
            for game_num in range(games_per_combination):
                game_result = self.simulate_game(combination, verbose=False)
                games_completed += 1
                
                if verbose and games_completed % 100 == 0:
                    print(f"Completed {games_completed}/{total_games} games ({games_completed/total_games*100:.1f}%)")
                
                # Update combination stats
                combo_stats['games_played'] += 1
                combo_stats['solve_attempts'] += game_result['solve_attempts']
                combo_stats['bankruptcies'] += game_result['bankruptcies']
                combo_stats['avg_turns'] += game_result['turns_taken']
                
                if game_result['winner'] >= 0:
                    combo_stats['wins_by_player'][game_result['winner']] += 1
                    combo_stats['successful_solves'] += 1
                
                for i in range(3):
                    combo_stats['total_winnings'][i] += game_result['final_winnings'][i]
                
                # Update individual AI stats
                for i, ai_type in enumerate(combination):
                    ai_stats = results['ai_performance'][ai_type]
                    ai_stats['games_played'] += 1
                    ai_stats['total_winnings'] += game_result['final_winnings'][i]
                    
                    if game_result['winner'] == i:
                        ai_stats['wins'] += 1
                    
                    # Note: solve attempts are tracked per game, not per AI
                    if i == 0:  # Only count once per game
                        ai_stats['solve_attempts'] += game_result['solve_attempts']
                        if game_result['winner'] >= 0:
                            ai_stats['successful_solves'] += 1
            
            # Calculate averages for this combination
            if combo_stats['games_played'] > 0:
                combo_stats['avg_turns'] /= combo_stats['games_played']
                for i in range(3):
                    combo_stats['avg_winnings'][i] = combo_stats['total_winnings'][i] / combo_stats['games_played']
        
        return results
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Generate a comprehensive report from tournament results."""
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("WHEEL OF FORTUNE AI TOURNAMENT RESULTS")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Overall AI Performance
        report_lines.append("INDIVIDUAL AI PERFORMANCE:")
        report_lines.append("-" * 40)
        
        ai_performance = results['ai_performance']
        for ai_type, stats in sorted(ai_performance.items()):
            if stats['games_played'] > 0:
                win_rate = stats['wins'] / stats['games_played'] * 100
                avg_winnings = stats['total_winnings'] / stats['games_played']
                solve_rate = stats['successful_solves'] / stats['games_played'] * 100 if stats['games_played'] > 0 else 0
                
                report_lines.append(f"{ai_type:20} | Win Rate: {win_rate:5.1f}% | Avg Winnings: ${avg_winnings:6.0f} | Solve Rate: {solve_rate:5.1f}%")
        
        report_lines.append("")
        report_lines.append("COMBINATION RESULTS:")
        report_lines.append("-" * 60)
        
        # Combination results
        for combo, stats in results['combinations'].items():
            report_lines.append(f"\n{combo}:")
            report_lines.append(f"  Games Played: {stats['games_played']}")
            report_lines.append(f"  Average Turns: {stats['avg_turns']:.1f}")
            report_lines.append(f"  Solve Attempts: {stats['solve_attempts']}")
            report_lines.append(f"  Successful Solves: {stats['successful_solves']}")
            report_lines.append(f"  Bankruptcies: {stats['bankruptcies']}")
            
            players = combo.split('-vs-')
            for i, player in enumerate(players):
                win_rate = stats['wins_by_player'][i] / stats['games_played'] * 100
                avg_winnings = stats['avg_winnings'][i]
                report_lines.append(f"    Player {i} ({player:15}): {stats['wins_by_player'][i]:4d} wins ({win_rate:5.1f}%) | Avg: ${avg_winnings:6.0f}")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to {output_file}")
        
        return report
    
    def save_detailed_csv(self, results: Dict[str, Any], filename: str):
        """Save detailed results to CSV for further analysis."""
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Combination', 'Player_0_Type', 'Player_1_Type', 'Player_2_Type',
                'Games_Played', 'Player_0_Wins', 'Player_1_Wins', 'Player_2_Wins',
                'Player_0_Win_Rate', 'Player_1_Win_Rate', 'Player_2_Win_Rate',
                'Player_0_Avg_Winnings', 'Player_1_Avg_Winnings', 'Player_2_Avg_Winnings',
                'Avg_Turns_Per_Game', 'Total_Solve_Attempts', 'Successful_Solves',
                'Solve_Success_Rate', 'Total_Bankruptcies'
            ])
            
            # Data rows
            for combo, stats in results['combinations'].items():
                players = combo.split('-vs-')
                
                win_rates = [
                    stats['wins_by_player'][i] / stats['games_played'] * 100 
                    for i in range(3)
                ]
                
                solve_success_rate = (
                    stats['successful_solves'] / stats['solve_attempts'] * 100 
                    if stats['solve_attempts'] > 0 else 0
                )
                
                writer.writerow([
                    combo, players[0], players[1], players[2],
                    stats['games_played'],
                    stats['wins_by_player'][0], stats['wins_by_player'][1], stats['wins_by_player'][2],
                    f"{win_rates[0]:.2f}", f"{win_rates[1]:.2f}", f"{win_rates[2]:.2f}",
                    f"{stats['avg_winnings'][0]:.0f}", f"{stats['avg_winnings'][1]:.0f}", f"{stats['avg_winnings'][2]:.0f}",
                    f"{stats['avg_turns']:.1f}", stats['solve_attempts'], stats['successful_solves'],
                    f"{solve_success_rate:.2f}", stats['bankruptcies']
                ])
        
        print(f"Detailed CSV saved to {filename}")


def main():
    """Run the solve timing experiments."""
    
    print("Starting Solve Timing AI Experiments...")
    print("This will run comprehensive simulations to evaluate AI performance.")
    print()
    
    simulator = GameSimulator()
    
    # Define test combinations
    # Test solve timing AIs against traditional AIs
    test_combinations = [
        # Solve timing AIs vs traditional AIs
        ['solve_timing', 'smart', 'conservative'],
        ['solve_conservative', 'smart', 'aggressive'],
        ['solve_aggressive', 'smart', 'conservative'],
        
        # All solve timing variants
        ['solve_timing', 'solve_conservative', 'solve_aggressive'],
        
        # Traditional AI baseline
        ['smart', 'conservative', 'aggressive'],
        
        # Head-to-head comparisons
        ['solve_timing', 'solve_timing', 'smart'],
        ['solve_conservative', 'solve_conservative', 'conservative'],
        ['solve_aggressive', 'solve_aggressive', 'aggressive'],
        
        # Mixed scenarios
        ['solve_timing', 'conservative', 'aggressive'],
        ['solve_aggressive', 'smart', 'smart'],
    ]
    
    # Run smaller test first
    print("Running quick test (100 games per combination)...")
    quick_results = simulator.run_tournament(test_combinations, games_per_combination=100, verbose=True)
    
    print("\nQuick Test Results:")
    print(simulator.generate_report(quick_results))
    
    # Ask user if they want to run full simulation
    response = input("\nRun full simulation (1000 games per combination)? This may take several minutes. (y/n): ")
    
    if response.lower().startswith('y'):
        print("\nRunning full tournament (1000 games per combination)...")
        full_results = simulator.run_tournament(test_combinations, games_per_combination=1000, verbose=True)
        
        # Generate outputs
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"solve_timing_report_{timestamp}.txt"
        csv_file = f"solve_timing_results_{timestamp}.csv"
        
        print(f"\nFull Tournament Results:")
        report = simulator.generate_report(full_results, report_file)
        print(report)
        
        simulator.save_detailed_csv(full_results, csv_file)
        
        print(f"\nFiles generated:")
        print(f"  - {report_file} (detailed report)")
        print(f"  - {csv_file} (CSV data for analysis)")
    
    else:
        print("Skipping full simulation.")
    
    print("\nExperiment complete!")


if __name__ == "__main__":
    main()