#!/usr/bin/env python3
"""
Test script to demonstrate the money optimization features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simulate the MoneyOptimizer class functionality in Python for testing
class MoneyOptimizerTest:
    def __init__(self):
        # Wheel configuration (24 sections)
        self.wheel_sections = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                              500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
        self.vowel_cost = 250
    
    def get_wheel_probabilities(self):
        total = len(self.wheel_sections)
        bankrupt_count = sum(1 for val in self.wheel_sections if val == -1)
        lose_turn_count = sum(1 for val in self.wheel_sections if val == 0)
        money_values = [val for val in self.wheel_sections if val > 0]
        
        return {
            'bankrupt_probability': bankrupt_count / total,
            'lose_turn_probability': lose_turn_count / total,
            'money_probability': len(money_values) / total,
            'average_money_value': sum(money_values) / len(money_values) if money_values else 0,
            'min_value': min(money_values) if money_values else 0,
            'max_value': max(money_values) if money_values else 0
        }
    
    def calculate_spin_expected_value(self, current_money, letter_probability=0.6):
        probs = self.get_wheel_probabilities()
        expected_gain = probs['money_probability'] * letter_probability * probs['average_money_value']
        expected_loss = probs['bankrupt_probability'] * current_money
        return expected_gain - expected_loss

def test_scenarios():
    optimizer = MoneyOptimizerTest()
    
    print("🎰 WHEEL OF FORTUNE MONEY OPTIMIZATION ANALYSIS")
    print("=" * 60)
    
    # Display wheel statistics
    probs = optimizer.get_wheel_probabilities()
    print(f"\n📊 WHEEL STATISTICS:")
    print(f"   • Bankrupt Probability: {probs['bankrupt_probability']:.1%}")
    print(f"   • Lose Turn Probability: {probs['lose_turn_probability']:.1%}")
    print(f"   • Money Probability: {probs['money_probability']:.1%}")
    print(f"   • Average Money Value: ${probs['average_money_value']:.0f}")
    print(f"   • Money Range: ${probs['min_value']} - ${probs['max_value']}")
    
    # Test different scenarios
    scenarios = [
        {"name": "Early Game (Low Money)", "money": 0, "letter_prob": 0.7},
        {"name": "Mid Game (Some Money)", "money": 500, "letter_prob": 0.6},
        {"name": "High Money (Risky)", "money": 1500, "letter_prob": 0.5},
        {"name": "Very High Money (Very Risky)", "money": 3000, "letter_prob": 0.4},
    ]
    
    print(f"\n💰 SCENARIO ANALYSIS:")
    print("-" * 60)
    
    for scenario in scenarios:
        money = scenario["money"]
        letter_prob = scenario["letter_prob"]
        expected_value = optimizer.calculate_spin_expected_value(money, letter_prob)
        potential_loss = probs['bankrupt_probability'] * money
        
        print(f"\n{scenario['name']}:")
        print(f"   Current Money: ${money}")
        print(f"   Letter Success Probability: {letter_prob:.1%}")
        print(f"   Expected Value of Spinning: ${expected_value:.0f}")
        print(f"   Potential Loss (Bankrupt): ${potential_loss:.0f}")
        
        # Recommendation
        if expected_value > 100:
            recommendation = "🟢 SPIN (High Expected Value)"
        elif expected_value > 0:
            recommendation = "🟡 SPIN (Positive Expected Value)"
        elif money > 250 and expected_value > -50:
            recommendation = "🟠 CONSIDER BUYING VOWEL"
        else:
            recommendation = "🔴 AVOID SPINNING (Negative Expected Value)"
        
        print(f"   Recommendation: {recommendation}")
    
    # Vowel vs Spin Analysis
    print(f"\n🔤 VOWEL vs SPIN ANALYSIS:")
    print("-" * 60)
    
    vowel_scenarios = [
        {"money": 250, "vowel_prob": 0.8},
        {"money": 500, "vowel_prob": 0.7},
        {"money": 1000, "vowel_prob": 0.6},
    ]
    
    for scenario in vowel_scenarios:
        money = scenario["money"]
        vowel_prob = scenario["vowel_prob"]
        
        spin_ev = optimizer.calculate_spin_expected_value(money, 0.6)
        vowel_ev = vowel_prob * 100 - optimizer.vowel_cost  # Simplified vowel EV
        
        print(f"\nMoney: ${money}, Vowel Probability: {vowel_prob:.1%}")
        print(f"   Spin Expected Value: ${spin_ev:.0f}")
        print(f"   Vowel Expected Value: ${vowel_ev:.0f}")
        
        if vowel_ev > spin_ev:
            print(f"   💡 Recommendation: BUY VOWEL (Better EV)")
        else:
            print(f"   💡 Recommendation: SPIN (Better EV)")
    
    # Risk Analysis
    print(f"\n⚠️  RISK ANALYSIS:")
    print("-" * 60)
    
    risk_levels = [
        {"money": 100, "description": "Low Risk"},
        {"money": 500, "description": "Medium Risk"},
        {"money": 1000, "description": "High Risk"},
        {"money": 2000, "description": "Very High Risk"},
    ]
    
    for risk in risk_levels:
        money = risk["money"]
        potential_loss = probs['bankrupt_probability'] * money
        risk_percentage = potential_loss / money if money > 0 else 0
        
        print(f"\n{risk['description']} (${money}):")
        print(f"   Potential Loss: ${potential_loss:.0f}")
        print(f"   Risk as % of Total: {risk_percentage:.1%}")
        
        if risk_percentage > 0.15:
            print(f"   ⚠️  WARNING: High risk of significant loss!")
        elif risk_percentage > 0.08:
            print(f"   ⚡ CAUTION: Moderate risk")
        else:
            print(f"   ✅ SAFE: Low risk")

if __name__ == "__main__":
    test_scenarios()