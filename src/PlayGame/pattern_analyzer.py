"""
Pattern-Based Word Analysis for Wheel of Fortune
Analyzes the current board state to suggest consonants based on likely word completions.
"""

import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict, Counter


class WordPatternAnalyzer:
    """Analyzes board patterns to suggest optimal consonants based on word completion probability."""
    
    def __init__(self):
        # Common word patterns and endings
        self.common_endings = {
            'ING': ['N', 'G'],
            'TION': ['T', 'N'],
            'SION': ['S', 'N'],
            'NESS': ['N', 'S'],
            'MENT': ['M', 'N', 'T'],
            'ABLE': ['B', 'L'],
            'IBLE': ['B', 'L'],
            'OUGH': ['G', 'H'],
            'IGHT': ['G', 'H', 'T'],
            'OULD': ['L', 'D'],
            'ANCE': ['N', 'C'],
            'ENCE': ['N', 'C'],
            'ALLY': ['L', 'Y'],
            'ULLY': ['L', 'Y'],
            'ERRY': ['R', 'Y'],
            'APPY': ['P', 'Y'],
        }
        
        # Common word beginnings
        self.common_beginnings = {
            'THE': ['T', 'H'],
            'AND': ['N', 'D'],
            'ING': ['N', 'G'],
            'HER': ['H', 'R'],
            'HAT': ['H', 'T'],
            'HIS': ['H', 'S'],
            'THA': ['T', 'H'],
            'ERE': ['R'],
            'FOR': ['F', 'R'],
            'ENT': ['N', 'T'],
            'ION': ['N'],
            'TER': ['T', 'R'],
            'WAS': ['W', 'S'],
            'YOU': ['Y'],
            'ITH': ['T', 'H'],
            'VER': ['V', 'R'],
            'ALL': ['L'],
            'WIT': ['W', 'T'],
            'THI': ['T', 'H'],
            'TIO': ['T'],
        }
        
        # Common letter combinations and their likely next letters
        self.bigram_patterns = {
            'TH': ['R', 'S', 'T', 'N'],
            'HE': ['R', 'N', 'S', 'T'],
            'IN': ['G', 'T', 'S', 'D'],
            'ER': ['S', 'T', 'N', 'Y'],
            'AN': ['D', 'T', 'S', 'Y'],
            'RE': ['S', 'D', 'N', 'T'],
            'ED': ['S', 'T', 'N'],
            'ND': ['S', 'T', 'N'],
            'OR': ['S', 'T', 'N', 'Y'],
            'AR': ['S', 'T', 'N', 'Y'],
            'AL': ['L', 'S', 'T', 'N'],
            'EN': ['T', 'S', 'D', 'G'],
            'AT': ['S', 'T', 'H', 'R'],
            'ON': ['S', 'T', 'G', 'D'],
            'OU': ['R', 'T', 'S', 'N'],
            'IT': ['S', 'T', 'H', 'Y'],
            'IS': ['S', 'T', 'H'],
            'TO': ['R', 'N', 'P', 'W'],
            'ST': ['R', 'S', 'T', 'Y'],
            'NG': ['S', 'T', 'H'],
        }
        
        # Common trigram patterns
        self.trigram_patterns = {
            'THE': ['R', 'S', 'M', 'N'],
            'AND': ['S', 'T'],
            'ING': ['S', 'T', 'H'],
            'HER': ['S', 'T', 'N'],
            'HAT': ['S', 'T'],
            'HIS': ['S', 'T'],
            'THA': ['T', 'N'],
            'ERE': ['S', 'T', 'D'],
            'FOR': ['S', 'T', 'M'],
            'ENT': ['S', 'T', 'R'],
            'ION': ['S', 'T'],
            'TER': ['S', 'T', 'N'],
            'OUR': ['S', 'T', 'N'],
            'YOU': ['R', 'S', 'T'],
            'ITH': ['S', 'T'],
            'VER': ['S', 'T', 'Y'],
            'ALL': ['S', 'T', 'Y'],
            'WIT': ['H', 'S', 'T'],
            'THI': ['S', 'T', 'N'],
            'TIO': ['N', 'S'],
        }
        
        # Common short words (2-4 letters)
        self.common_short_words = {
            2: ['TO', 'OF', 'IN', 'IT', 'IS', 'BE', 'AS', 'AT', 'SO', 'WE', 'HE', 'BY', 'OR', 'ON', 'DO', 'IF', 'ME', 'MY', 'UP', 'AN', 'GO', 'NO', 'US', 'AM'],
            3: ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'WAY', 'TOO', 'ANY', 'SHE', 'USE'],
            4: ['THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'KNOW', 'WANT', 'BEEN', 'GOOD', 'MUCH', 'SOME', 'TIME', 'VERY', 'WHEN', 'COME', 'HERE', 'JUST', 'LIKE', 'LONG', 'MAKE', 'MANY', 'OVER', 'SUCH', 'TAKE', 'THAN', 'THEM', 'WELL', 'WERE']
        }
    
    def analyze_board_patterns(self, showing: str, previous_guesses: List[str]) -> Dict[str, float]:
        """
        Analyze the current board state and return consonant suggestions with confidence scores.
        
        Args:
            showing: Current puzzle state with blanks as underscores
            previous_guesses: List of already guessed letters
            
        Returns:
            Dictionary mapping consonants to confidence scores (0-1)
        """
        consonant_scores = defaultdict(float)
        available_consonants = set('BCDFGHJKLMNPQRSTVWXYZ') - set(previous_guesses)
        
        if not available_consonants:
            return {}
        
        # Split into words for analysis
        words = showing.split(' ')
        
        for word in words:
            if len(word) == 0:
                continue
                
            # Analyze each word for patterns
            word_scores = self._analyze_word_patterns(word, available_consonants)
            
            # Weight scores based on word length and completion
            completion_ratio = (len(word) - word.count('_')) / len(word) if len(word) > 0 else 0
            weight = 1.0 + (completion_ratio * 2)  # More complete words get higher weight
            
            for consonant, score in word_scores.items():
                consonant_scores[consonant] += score * weight
        
        # Normalize scores
        if consonant_scores:
            max_score = max(consonant_scores.values())
            if max_score > 0:
                consonant_scores = {c: score / max_score for c, score in consonant_scores.items()}
        
        return dict(consonant_scores)
    
    def _analyze_word_patterns(self, word: str, available_consonants: Set[str]) -> Dict[str, float]:
        """Analyze a single word for letter patterns."""
        scores = defaultdict(float)
        word_len = len(word)
        
        # Skip very short words or words with no blanks
        if word_len < 2 or '_' not in word:
            return scores
        
        # Check for common short word patterns
        if word_len <= 4:
            short_word_scores = self._analyze_short_word_patterns(word, available_consonants)
            for consonant, score in short_word_scores.items():
                scores[consonant] += score * 2.0  # Higher weight for short words
        
        # Check for ending patterns
        ending_scores = self._analyze_ending_patterns(word, available_consonants)
        for consonant, score in ending_scores.items():
            scores[consonant] += score * 1.5
        
        # Check for beginning patterns
        beginning_scores = self._analyze_beginning_patterns(word, available_consonants)
        for consonant, score in beginning_scores.items():
            scores[consonant] += score * 1.5
        
        # Check for bigram patterns
        bigram_scores = self._analyze_bigram_patterns(word, available_consonants)
        for consonant, score in bigram_scores.items():
            scores[consonant] += score
        
        # Check for trigram patterns
        trigram_scores = self._analyze_trigram_patterns(word, available_consonants)
        for consonant, score in trigram_scores.items():
            scores[consonant] += score * 1.2
        
        return scores
    
    def _analyze_short_word_patterns(self, word: str, available_consonants: Set[str]) -> Dict[str, float]:
        """Analyze patterns for short words (2-4 letters)."""
        scores = defaultdict(float)
        word_len = len(word)
        
        if word_len not in self.common_short_words:
            return scores
        
        # Create a pattern from the current word state
        pattern = word.replace('_', '.')
        
        # Check against common short words
        for common_word in self.common_short_words[word_len]:
            if re.match(pattern, common_word):
                # Find missing consonants
                for i, (current, target) in enumerate(zip(word, common_word)):
                    if current == '_' and target in available_consonants:
                        scores[target] += 0.8  # High confidence for short word matches
        
        return scores
    
    def _analyze_ending_patterns(self, word: str, available_consonants: Set[str]) -> Dict[str, float]:
        """Analyze word ending patterns."""
        scores = defaultdict(float)
        
        # Look at the last 3-5 characters for ending patterns
        for length in range(3, min(6, len(word) + 1)):
            ending = word[-length:]
            
            # Check if this ending matches any known patterns
            for pattern, likely_consonants in self.common_endings.items():
                if self._matches_pattern(ending, pattern):
                    for consonant in likely_consonants:
                        if consonant in available_consonants:
                            scores[consonant] += 0.6
        
        return scores
    
    def _analyze_beginning_patterns(self, word: str, available_consonants: Set[str]) -> Dict[str, float]:
        """Analyze word beginning patterns."""
        scores = defaultdict(float)
        
        # Look at the first 3-5 characters for beginning patterns
        for length in range(3, min(6, len(word) + 1)):
            beginning = word[:length]
            
            # Check if this beginning matches any known patterns
            for pattern, likely_consonants in self.common_beginnings.items():
                if self._matches_pattern(beginning, pattern):
                    for consonant in likely_consonants:
                        if consonant in available_consonants:
                            scores[consonant] += 0.6
        
        return scores
    
    def _analyze_bigram_patterns(self, word: str, available_consonants: Set[str]) -> Dict[str, float]:
        """Analyze bigram (2-letter) patterns in the word."""
        scores = defaultdict(float)
        
        for i in range(len(word) - 1):
            bigram = word[i:i+2]
            
            # Skip if contains blanks in the middle
            if '_' in bigram:
                continue
                
            if bigram in self.bigram_patterns:
                # Look for positions where we can add the suggested letters
                for j in range(max(0, i-1), min(len(word), i+3)):
                    if j < len(word) and word[j] == '_':
                        for consonant in self.bigram_patterns[bigram]:
                            if consonant in available_consonants:
                                scores[consonant] += 0.4
        
        return scores
    
    def _analyze_trigram_patterns(self, word: str, available_consonants: Set[str]) -> Dict[str, float]:
        """Analyze trigram (3-letter) patterns in the word."""
        scores = defaultdict(float)
        
        for i in range(len(word) - 2):
            trigram = word[i:i+3]
            
            # Skip if contains blanks
            if '_' in trigram:
                continue
                
            if trigram in self.trigram_patterns:
                # Look for positions where we can add the suggested letters
                for j in range(max(0, i-1), min(len(word), i+4)):
                    if j < len(word) and word[j] == '_':
                        for consonant in self.trigram_patterns[trigram]:
                            if consonant in available_consonants:
                                scores[consonant] += 0.5
        
        return scores
    
    def _matches_pattern(self, word_part: str, pattern: str) -> bool:
        """Check if a word part matches a pattern, allowing for blanks."""
        if len(word_part) != len(pattern):
            return False
        
        for w, p in zip(word_part, pattern):
            if w != '_' and w != p:
                return False
        
        return True
    
    def get_top_consonant_suggestions(self, showing: str, previous_guesses: List[str], num_suggestions: int = 3) -> List[Tuple[str, float, str]]:
        """
        Get the top consonant suggestions with explanations.
        
        Args:
            showing: Current puzzle state
            previous_guesses: Already guessed letters
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of tuples (consonant, confidence_score, explanation)
        """
        consonant_scores = self.analyze_board_patterns(showing, previous_guesses)
        
        if not consonant_scores:
            # Fallback to frequency-based suggestions
            fallback_consonants = ['T', 'N', 'S', 'H', 'R', 'D', 'L', 'C', 'M', 'W', 'F', 'G', 'Y', 'P', 'B']
            available = [c for c in fallback_consonants if c not in previous_guesses]
            return [(c, 0.5, "Frequency-based suggestion") for c in available[:num_suggestions]]
        
        # Sort by score and get top suggestions
        sorted_consonants = sorted(consonant_scores.items(), key=lambda x: x[1], reverse=True)
        
        suggestions = []
        for consonant, score in sorted_consonants[:num_suggestions]:
            explanation = self._generate_explanation(consonant, showing, previous_guesses)
            suggestions.append((consonant, score, explanation))
        
        return suggestions
    
    def _generate_explanation(self, consonant: str, showing: str, previous_guesses: List[str]) -> str:
        """Generate an explanation for why this consonant is suggested."""
        words = showing.split(' ')
        reasons = []
        
        for word in words:
            if '_' not in word or len(word) < 2:
                continue
                
            # Check for specific pattern matches
            word_len = len(word)
            
            # Check short words
            if word_len <= 4 and word_len in self.common_short_words:
                pattern = word.replace('_', '.')
                for common_word in self.common_short_words[word_len]:
                    if re.match(pattern, common_word) and consonant in common_word:
                        reasons.append(f"Completes common word '{common_word}'")
                        break
            
            # Check endings
            for length in range(3, min(6, len(word) + 1)):
                ending = word[-length:]
                for pattern, likely_consonants in self.common_endings.items():
                    if consonant in likely_consonants and self._matches_pattern(ending, pattern):
                        reasons.append(f"Common ending pattern '{pattern}'")
                        break
            
            # Check beginnings
            for length in range(3, min(6, len(word) + 1)):
                beginning = word[:length]
                for pattern, likely_consonants in self.common_beginnings.items():
                    if consonant in likely_consonants and self._matches_pattern(beginning, pattern):
                        reasons.append(f"Common beginning pattern '{pattern}'")
                        break
        
        if not reasons:
            return "Pattern-based analysis"
        
        return "; ".join(reasons[:2])  # Limit to top 2 reasons


# Test the pattern analyzer
if __name__ == "__main__":
    analyzer = WordPatternAnalyzer()
    
    test_cases = [
        {
            'showing': 'T_E _U_C_ _RO__ _O_',
            'previous_guesses': ['T', 'E', 'C', 'O'],
            'description': 'Mid-game puzzle'
        },
        {
            'showing': '_ _ _ _ _',
            'previous_guesses': [],
            'description': 'Fresh puzzle'
        },
        {
            'showing': 'TH_ QU_CK _RO_N _O_',
            'previous_guesses': ['T', 'H', 'Q', 'U', 'C', 'K', 'R', 'O', 'N'],
            'description': 'Nearly complete puzzle'
        },
        {
            'showing': '_ING _O_ET_ING',
            'previous_guesses': ['I', 'N', 'G', 'O', 'E', 'T'],
            'description': 'Pattern with common endings'
        }
    ]
    
    print("Pattern-Based Consonant Analysis Test Results:")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Puzzle: {test['showing']}")
        print(f"Previous guesses: {test['previous_guesses']}")
        
        suggestions = analyzer.get_top_consonant_suggestions(
            test['showing'], 
            test['previous_guesses'], 
            num_suggestions=3
        )
        
        print("Top consonant suggestions:")
        for j, (consonant, confidence, explanation) in enumerate(suggestions, 1):
            print(f"  {j}. {consonant} (confidence: {confidence:.2f}) - {explanation}")