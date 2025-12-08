/**
 * Wheel of Fortune Money Optimization Engine
 * Provides strategic decision-making based on expected value calculations
 */

class MoneyOptimizer {
    constructor() {
        // Wheel configuration (24 sections, matching create_accurate_wheel.py)
        // 0 = LOSE TURN, -1 = BANKRUPT
        this.wheelSections = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                             500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600];
        
        // Letter frequency in English (for consonant suggestions)
        this.letterFrequency = {
            'T': 9.056, 'N': 6.749, 'S': 6.327, 'H': 6.094, 'R': 5.987,
            'D': 4.253, 'L': 4.025, 'C': 2.782, 'M': 2.406, 'W': 2.360,
            'F': 2.228, 'G': 2.015, 'Y': 1.974, 'P': 1.929, 'B': 1.292,
            'V': 0.978, 'K': 0.772, 'J': 0.153, 'X': 0.150, 'Q': 0.095, 'Z': 0.074
        };
        
        // Common letter patterns in Wheel of Fortune puzzles
        this.commonPatterns = {
            'THE': 3.5, 'AND': 2.8, 'ING': 2.1, 'HER': 1.8, 'HAT': 1.6,
            'HIS': 1.5, 'THA': 1.4, 'ERE': 1.3, 'FOR': 1.2, 'ENT': 1.1
        };
        
        this.vowelCost = 250;
        this.solveBonusMultiplier = 1.5; // Bonus for solving puzzle
    }

    /**
     * Calculate wheel probabilities
     */
    getWheelProbabilities() {
        const total = this.wheelSections.length;
        const bankruptCount = this.wheelSections.filter(val => val === -1).length;
        const loseTurnCount = this.wheelSections.filter(val => val === 0).length;
        const moneyValues = this.wheelSections.filter(val => val > 0);
        
        return {
            bankruptProbability: bankruptCount / total,
            loseTurnProbability: loseTurnCount / total,
            moneyProbability: moneyValues.length / total,
            averageMoneyValue: moneyValues.reduce((sum, val) => sum + val, 0) / moneyValues.length,
            minValue: Math.min(...moneyValues),
            maxValue: Math.max(...moneyValues),
            bankruptCount,
            loseTurnCount,
            totalSections: total
        };
    }

    /**
     * Calculate expected value of spinning the wheel
     */
    calculateSpinExpectedValue(currentMoney, letterProbability = 0.6) {
        const probs = this.getWheelProbabilities();
        
        // Expected value calculation:
        // EV = P(money) * P(letter_in_puzzle) * avg_money_value - P(bankrupt) * current_money
        const expectedGain = probs.moneyProbability * letterProbability * probs.averageMoneyValue;
        const expectedLoss = probs.bankruptProbability * currentMoney;
        
        return {
            expectedValue: expectedGain - expectedLoss,
            expectedGain,
            expectedLoss,
            probabilities: probs
        };
    }

    /**
     * Calculate expected value of buying a vowel
     */
    calculateVowelExpectedValue(currentMoney, vowelProbability = 0.7) {
        // Cost is fixed at $250
        // Benefit is keeping your turn if vowel is in puzzle
        const expectedBenefit = vowelProbability * 100; // Estimated benefit of keeping turn
        
        return {
            expectedValue: expectedBenefit - this.vowelCost,
            cost: this.vowelCost,
            expectedBenefit,
            canAfford: currentMoney >= this.vowelCost
        };
    }

    /**
     * Analyze letter frequency in current puzzle state
     */
    analyzeLetterProbabilities(revealedLetters, usedLetters, category = '') {
        const puzzle = revealedLetters.join('');
        const availableConsonants = [];
        const availableVowels = [];
        
        // Get available letters
        for (let letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
            if (!usedLetters.includes(letter)) {
                if ('AEIOU'.includes(letter)) {
                    availableVowels.push(letter);
                } else {
                    availableConsonants.push(letter);
                }
            }
        }

        // Score consonants based on frequency and pattern matching
        const consonantScores = availableConsonants.map(letter => {
            let score = this.letterFrequency[letter] || 1;
            
            // Boost score based on common patterns
            const patternBoost = this.calculatePatternBoost(letter, puzzle, category);
            score += patternBoost;
            
            // Boost score for letters that commonly appear together with revealed letters
            const contextBoost = this.calculateContextBoost(letter, revealedLetters);
            score += contextBoost;
            
            return { letter, score, probability: Math.min(score / 15, 0.9) };
        }).sort((a, b) => b.score - a.score);

        // Score vowels
        const vowelScores = availableVowels.map(letter => {
            let score = letter === 'E' ? 8 : letter === 'A' ? 6 : letter === 'I' ? 4 : 
                       letter === 'O' ? 4 : 2; // U is least common
            
            const contextBoost = this.calculateContextBoost(letter, revealedLetters);
            score += contextBoost;
            
            return { letter, score, probability: Math.min(score / 12, 0.8) };
        }).sort((a, b) => b.score - a.score);

        return {
            consonants: consonantScores,
            vowels: vowelScores,
            topConsonants: consonantScores.slice(0, 2),
            topVowel: vowelScores[0]
        };
    }

    /**
     * Calculate pattern-based boost for letter probability
     */
    calculatePatternBoost(letter, puzzle, category) {
        let boost = 0;
        
        // Category-specific boosts
        if (category.includes('PHRASE')) {
            if (['T', 'H', 'E', 'R', 'S'].includes(letter)) boost += 2;
        } else if (category.includes('PERSON')) {
            if (['N', 'R', 'S', 'T'].includes(letter)) boost += 2;
        } else if (category.includes('PLACE')) {
            if (['N', 'T', 'R', 'S'].includes(letter)) boost += 2;
        }
        
        // Common ending patterns
        if (puzzle.includes('_ING')) {
            if (letter === 'T' || letter === 'S' || letter === 'R') boost += 3;
        }
        
        if (puzzle.includes('TH_')) {
            if (letter === 'E' || letter === 'A' || letter === 'I') boost += 3;
        }
        
        return boost;
    }

    /**
     * Calculate context-based boost for letter probability
     */
    calculateContextBoost(letter, revealedLetters) {
        let boost = 0;
        const puzzle = revealedLetters.join('');
        
        // Look for common letter combinations
        const commonPairs = {
            'T': ['H', 'R', 'S'], 'H': ['T', 'E', 'R'], 'R': ['T', 'S', 'E'],
            'S': ['T', 'H', 'R'], 'N': ['T', 'G', 'D'], 'L': ['L', 'E', 'Y']
        };
        
        if (commonPairs[letter]) {
            for (let pair of commonPairs[letter]) {
                if (puzzle.includes(pair)) boost += 1;
            }
        }
        
        return boost;
    }

    /**
     * Calculate risk vs reward for current situation
     */
    calculateRiskReward(currentMoney, opponentScores, roundsRemaining) {
        const maxOpponentScore = Math.max(...opponentScores);
        const scoreDifference = currentMoney - maxOpponentScore;
        
        // Risk assessment
        const bankruptRisk = this.getWheelProbabilities().bankruptProbability;
        const potentialLoss = currentMoney * bankruptRisk;
        
        // Reward assessment
        const spinEV = this.calculateSpinExpectedValue(currentMoney);
        
        // Strategic considerations
        const isLeading = scoreDifference > 0;
        const isFarBehind = scoreDifference < -1000;
        const isCloseGame = Math.abs(scoreDifference) < 500;
        
        return {
            riskLevel: potentialLoss > currentMoney * 0.3 ? 'HIGH' : 
                      potentialLoss > currentMoney * 0.15 ? 'MEDIUM' : 'LOW',
            potentialLoss,
            expectedReward: spinEV.expectedValue,
            riskRewardRatio: spinEV.expectedValue / Math.max(potentialLoss, 1),
            strategicPosition: isLeading ? 'LEADING' : isFarBehind ? 'FAR_BEHIND' : 'COMPETITIVE',
            recommendation: this.getStrategicRecommendation(isLeading, isFarBehind, isCloseGame, currentMoney, spinEV)
        };
    }

    /**
     * Get strategic recommendation based on game state
     */
    getStrategicRecommendation(isLeading, isFarBehind, isCloseGame, currentMoney, spinEV) {
        if (isLeading && currentMoney > 1000) {
            return 'CONSERVATIVE'; // Protect lead, consider buying vowels
        } else if (isFarBehind) {
            return 'AGGRESSIVE'; // Take risks to catch up
        } else if (isCloseGame) {
            return 'BALANCED'; // Mix of strategies
        } else {
            return spinEV.expectedValue > 0 ? 'SPIN' : 'CONSERVATIVE';
        }
    }

    /**
     * Calculate solve probability and expected value
     */
    calculateSolveExpectedValue(revealedLetters, currentMoney, totalPossibleWinnings) {
        const puzzle = revealedLetters.join('');
        const revealedCount = revealedLetters.filter(letter => letter !== '_').length;
        const totalLetters = revealedLetters.length;
        const completionRatio = revealedCount / totalLetters;
        
        // Estimate solve probability based on completion ratio
        let solveProbability = 0;
        if (completionRatio >= 0.8) solveProbability = 0.9;
        else if (completionRatio >= 0.6) solveProbability = 0.7;
        else if (completionRatio >= 0.4) solveProbability = 0.4;
        else if (completionRatio >= 0.2) solveProbability = 0.2;
        else solveProbability = 0.05;
        
        // Boost probability if common patterns are visible
        if (puzzle.includes('THE') || puzzle.includes('AND') || puzzle.includes('ING')) {
            solveProbability += 0.1;
        }
        
        const expectedWinnings = currentMoney * this.solveBonusMultiplier;
        const expectedValue = solveProbability * expectedWinnings;
        
        return {
            solveProbability: Math.min(solveProbability, 0.95),
            expectedValue,
            expectedWinnings,
            completionRatio,
            shouldAttempt: solveProbability > 0.6 || (completionRatio > 0.7 && currentMoney > 500)
        };
    }

    /**
     * Main strategy recommendation engine
     */
    getOptimalStrategy(gameState) {
        const {
            currentMoney,
            revealedLetters,
            usedLetters,
            opponentScores,
            roundsRemaining,
            category
        } = gameState;

        // Analyze current situation
        const letterAnalysis = this.analyzeLetterProbabilities(revealedLetters, usedLetters, category);
        const spinEV = this.calculateSpinExpectedValue(currentMoney, letterAnalysis.topConsonants[0]?.probability || 0.6);
        const vowelEV = this.calculateVowelExpectedValue(currentMoney, letterAnalysis.topVowel?.probability || 0.7);
        const solveEV = this.calculateSolveExpectedValue(revealedLetters, currentMoney, currentMoney * 2);
        const riskReward = this.calculateRiskReward(currentMoney, opponentScores, roundsRemaining);

        // Decision logic
        let recommendation = 'SPIN';
        let reasoning = [];

        // Check if we should solve
        if (solveEV.shouldAttempt) {
            recommendation = 'SOLVE';
            reasoning.push(`High solve probability (${(solveEV.solveProbability * 100).toFixed(1)}%)`);
            reasoning.push(`Expected value: $${solveEV.expectedValue.toFixed(0)}`);
        }
        // Check if we should buy a vowel
        else if (vowelEV.canAfford && letterAnalysis.topVowel && 
                 vowelEV.expectedValue > spinEV.expectedValue && 
                 letterAnalysis.topVowel.probability > 0.6) {
            recommendation = 'BUY_VOWEL';
            reasoning.push(`High vowel probability (${(letterAnalysis.topVowel.probability * 100).toFixed(1)}%)`);
            reasoning.push(`Better expected value than spinning ($${vowelEV.expectedValue.toFixed(0)} vs $${spinEV.expectedValue.toFixed(0)})`);
        }
        // Default to spinning with risk considerations
        else {
            if (riskReward.riskLevel === 'HIGH' && riskReward.strategicPosition === 'LEADING') {
                recommendation = 'BUY_VOWEL';
                reasoning.push('High risk detected while leading - consider safer vowel purchase');
            } else {
                recommendation = 'SPIN';
                reasoning.push(`Expected value: $${spinEV.expectedValue.toFixed(0)}`);
                reasoning.push(`Risk level: ${riskReward.riskLevel}`);
            }
        }

        return {
            recommendation,
            reasoning,
            analysis: {
                spin: spinEV,
                vowel: vowelEV,
                solve: solveEV,
                risk: riskReward,
                letters: letterAnalysis
            },
            suggestedConsonants: letterAnalysis.topConsonants.slice(0, 2),
            suggestedVowel: letterAnalysis.topVowel,
            wheelProbabilities: this.getWheelProbabilities()
        };
    }

    /**
     * Format strategy advice for display
     */
    formatAdvice(strategy) {
        const advice = {
            action: strategy.recommendation,
            reasoning: strategy.reasoning,
            wheelStats: {
                bankruptChance: `${(strategy.wheelProbabilities.bankruptProbability * 100).toFixed(1)}%`,
                loseTurnChance: `${(strategy.wheelProbabilities.loseTurnProbability * 100).toFixed(1)}%`,
                expectedSpinValue: `$${strategy.analysis.spin.expectedValue.toFixed(0)}`,
                averageWheelValue: `$${strategy.wheelProbabilities.averageMoneyValue.toFixed(0)}`
            },
            letterSuggestions: {
                consonants: strategy.suggestedConsonants.map(c => 
                    `${c.letter} (${(c.probability * 100).toFixed(1)}% likely)`
                ),
                vowel: strategy.suggestedVowel ? 
                    `${strategy.suggestedVowel.letter} (${(strategy.suggestedVowel.probability * 100).toFixed(1)}% likely)` : 
                    'No vowels available'
            }
        };

        return advice;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MoneyOptimizer;
}