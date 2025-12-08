#!/usr/bin/env python3
"""
Enhanced Wheel of Fortune Backend with Money Optimization for AI Players
"""

import csv
import json
import random
import re
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Load puzzle data (same as original backend.py)
def load_puzzles():
    puzzles = []
    puzzle_file = os.path.join('data', 'puzzles', 'valid.csv')
    
    if not os.path.exists(puzzle_file):
        return [
            {"phrase": "WHEEL OF FORTUNE", "category": "TV SHOW"},
            {"phrase": "GOOD LUCK", "category": "PHRASE"},
            {"phrase": "HAPPY BIRTHDAY", "category": "EVENT"}
        ]
    
    try:
        with open(puzzle_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    phrase = row[0].strip().upper()
                    category = row[1].strip().upper()
                    if re.match(r'^[A-Z\s&\'-]+$', phrase) and len(phrase) <= 50:
                        puzzles.append({
                            "phrase": phrase,
                            "category": category
                        })
    except Exception as e:
        print(f"Error loading puzzles: {e}")
        return [
            {"phrase": "WHEEL OF FORTUNE", "category": "TV SHOW"},
            {"phrase": "GOOD LUCK", "category": "PHRASE"},
            {"phrase": "HAPPY BIRTHDAY", "category": "EVENT"}
        ]
    
    return puzzles[:500]

PUZZLES = load_puzzles()

class MoneyOptimizedAI:
    """AI Player with money optimization logic"""
    
    def __init__(self, strategy='optimized'):
        self.strategy = strategy
        
        # Wheel configuration (matching frontend)
        self.wheel_sections = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                              500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
        
        # Letter frequency in English
        self.letter_frequency = {
            'T': 9.056, 'N': 6.749, 'S': 6.327, 'H': 6.094, 'R': 5.987,
            'D': 4.253, 'L': 4.025, 'C': 2.782, 'M': 2.406, 'W': 2.360,
            'F': 2.228, 'G': 2.015, 'Y': 1.974, 'P': 1.929, 'B': 1.292,
            'V': 0.978, 'K': 0.772, 'J': 0.153, 'X': 0.150, 'Q': 0.095, 'Z': 0.074
        }
        
        self.vowel_cost = 250
    
    def get_wheel_probabilities(self):
        """Calculate wheel probabilities"""
        total = len(self.wheel_sections)
        bankrupt_count = sum(1 for val in self.wheel_sections if val == -1)
        lose_turn_count = sum(1 for val in self.wheel_sections if val == 0)
        money_values = [val for val in self.wheel_sections if val > 0]
        
        return {
            'bankrupt_probability': bankrupt_count / total,
            'lose_turn_probability': lose_turn_count / total,
            'money_probability': len(money_values) / total,
            'average_money_value': sum(money_values) / len(money_values) if money_values else 0
        }
    
    def calculate_spin_expected_value(self, current_money, letter_probability=0.6):
        """Calculate expected value of spinning"""
        probs = self.get_wheel_probabilities()
        
        expected_gain = probs['money_probability'] * letter_probability * probs['average_money_value']
        expected_loss = probs['bankrupt_probability'] * current_money
        
        return expected_gain - expected_loss
    
    def analyze_letter_probabilities(self, revealed_letters, used_letters, category=''):
        """Analyze letter probabilities for current puzzle state"""
        puzzle = ''.join(revealed_letters)
        available_consonants = []
        available_vowels = []
        
        # Get available letters
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if letter not in used_letters:
                if letter in 'AEIOU':
                    available_vowels.append(letter)
                else:
                    available_consonants.append(letter)
        
        # Score consonants based on frequency and patterns
        consonant_scores = []
        for letter in available_consonants:
            score = self.letter_frequency.get(letter, 1)
            
            # Category-specific boosts
            if 'PHRASE' in category:
                if letter in ['T', 'H', 'E', 'R', 'S']:
                    score += 2
            elif 'PERSON' in category:
                if letter in ['N', 'R', 'S', 'T']:
                    score += 2
            
            # Pattern boosts
            if '_ING' in puzzle and letter in ['T', 'S', 'R']:
                score += 3
            if 'TH_' in puzzle and letter in ['E', 'A', 'I']:
                score += 3
            
            probability = min(score / 15, 0.9)
            consonant_scores.append({'letter': letter, 'score': score, 'probability': probability})
        
        consonant_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Score vowels
        vowel_scores = []
        for letter in available_vowels:
            score = {'E': 8, 'A': 6, 'I': 4, 'O': 4, 'U': 2}.get(letter, 2)
            probability = min(score / 12, 0.8)
            vowel_scores.append({'letter': letter, 'score': score, 'probability': probability})
        
        vowel_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'consonants': consonant_scores,
            'vowels': vowel_scores,
            'top_consonants': consonant_scores[:2],
            'top_vowel': vowel_scores[0] if vowel_scores else None
        }
    
    def calculate_solve_probability(self, revealed_letters):
        """Calculate probability of successfully solving puzzle"""
        puzzle = ''.join(revealed_letters)
        revealed_count = sum(1 for letter in revealed_letters if letter != '_')
        total_letters = len(revealed_letters)
        completion_ratio = revealed_count / total_letters if total_letters > 0 else 0
        
        # Base probability on completion ratio
        if completion_ratio >= 0.8:
            solve_probability = 0.9
        elif completion_ratio >= 0.6:
            solve_probability = 0.7
        elif completion_ratio >= 0.4:
            solve_probability = 0.4
        elif completion_ratio >= 0.2:
            solve_probability = 0.2
        else:
            solve_probability = 0.05
        
        # Boost for common patterns
        if 'THE' in puzzle or 'AND' in puzzle or 'ING' in puzzle:
            solve_probability += 0.1
        
        return min(solve_probability, 0.95)
    
    def get_optimal_move(self, revealed_letters, used_letters, current_money, puzzle_category, opponent_scores=None):
        """Get optimal move based on money optimization"""
        
        # Analyze current situation
        letter_analysis = self.analyze_letter_probabilities(revealed_letters, used_letters, puzzle_category)
        spin_ev = self.calculate_spin_expected_value(current_money, 
                                                   letter_analysis['top_consonants'][0]['probability'] if letter_analysis['top_consonants'] else 0.6)
        solve_probability = self.calculate_solve_probability(revealed_letters)
        
        # Decision logic
        
        # 1. Check if we should solve (high probability)
        if solve_probability > 0.7:
            return {'action': 'solve', 'solution': self._attempt_solve(revealed_letters, puzzle_category)}
        
        # 2. Check if we should buy a vowel
        if (current_money >= self.vowel_cost and 
            letter_analysis['top_vowel'] and 
            letter_analysis['top_vowel']['probability'] > 0.6):
            
            # Buy vowel if it's safer than spinning or if we have lots of money
            vowel_ev = letter_analysis['top_vowel']['probability'] * 100 - self.vowel_cost
            if vowel_ev > spin_ev or current_money > 1000:
                return {'action': 'buy_vowel', 'letter': letter_analysis['top_vowel']['letter']}
        
        # 3. Default to guessing consonant (requires spinning first)
        if letter_analysis['top_consonants']:
            return {'action': 'guess_consonant', 'letter': letter_analysis['top_consonants'][0]['letter']}
        
        # 4. Fallback to solving if no good letters left
        return {'action': 'solve', 'solution': self._attempt_solve(revealed_letters, puzzle_category)}
    
    def _attempt_solve(self, revealed_letters, category):
        """Attempt to solve puzzle - simplified version"""
        # In a real implementation, this would use advanced pattern matching
        # For now, return a placeholder that indicates AI is attempting to solve
        return "AI_SOLVE_ATTEMPT"

# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'wheel-of-fortune-new.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/puzzles/random')
def get_random_puzzle():
    """Get a random puzzle"""
    puzzle = random.choice(PUZZLES)
    return jsonify(puzzle)

@app.route('/api/puzzles/count')
def get_puzzle_count():
    """Get total number of available puzzles"""
    return jsonify({'count': len(PUZZLES)})

@app.route('/api/ai/move', methods=['POST'])
def get_ai_move():
    """Get AI player's next move using money optimization"""
    data = request.json
    
    strategy = data.get('strategy', 'optimized')
    revealed_letters = data.get('revealed_letters', [])
    used_letters = data.get('used_letters', [])
    current_money = data.get('current_money', 0)
    puzzle_category = data.get('puzzle_category', '')
    opponent_scores = data.get('opponent_scores', [])
    
    # Create AI player and get optimal move
    ai_player = MoneyOptimizedAI(strategy)
    move = ai_player.get_optimal_move(
        revealed_letters, 
        used_letters, 
        current_money, 
        puzzle_category,
        opponent_scores
    )
    
    return jsonify(move)

@app.route('/api/strategy/analyze', methods=['POST'])
def analyze_strategy():
    """Analyze current game state and provide strategy recommendations"""
    data = request.json
    
    revealed_letters = data.get('revealed_letters', [])
    used_letters = data.get('used_letters', [])
    current_money = data.get('current_money', 0)
    puzzle_category = data.get('puzzle_category', '')
    opponent_scores = data.get('opponent_scores', [])
    
    ai_player = MoneyOptimizedAI()
    
    # Get comprehensive analysis
    letter_analysis = ai_player.analyze_letter_probabilities(revealed_letters, used_letters, puzzle_category)
    wheel_probs = ai_player.get_wheel_probabilities()
    spin_ev = ai_player.calculate_spin_expected_value(current_money)
    solve_prob = ai_player.calculate_solve_probability(revealed_letters)
    
    analysis = {
        'wheel_probabilities': wheel_probs,
        'spin_expected_value': spin_ev,
        'solve_probability': solve_prob,
        'letter_analysis': letter_analysis,
        'recommended_action': ai_player.get_optimal_move(
            revealed_letters, used_letters, current_money, puzzle_category, opponent_scores
        )
    }
    
    return jsonify(analysis)

if __name__ == '__main__':
    print(f"Loaded {len(PUZZLES)} puzzles")
    print("Starting Enhanced Money-Optimized Wheel of Fortune Backend...")
    app.run(host='0.0.0.0', port=12001, debug=True)