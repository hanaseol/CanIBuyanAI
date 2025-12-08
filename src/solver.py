# src/solver.py
import re
from pathlib import Path
from collections import Counter
from math import log

def _normalize_pattern(pattern):
    if isinstance(pattern, list):
        return "".join(pattern).upper()
    s = str(pattern).upper()
    s = re.sub(r"[^A-Z _]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _load_candidates(puzzles_file="data/bonus_puzzles.txt"):
    p = Path(puzzles_file)
    if not p.exists():
        return []
    return [line.strip().upper() for line in p.read_text().splitlines() if line.strip()]

def _pattern_to_regex(pattern_str):
    parts = []
    for ch in pattern_str:
        if ch == " ":
            parts.append(r"\s")
        elif ch == "_":
            parts.append(".")
        else:
            parts.append(re.escape(ch))
    regex = "^" + "".join(parts) + "$"
    regex = regex.replace(r"\s", " ")
    return re.compile(regex)

def _letter_frequency(corpus):
    # corpus: list of phrases -> flatten letters and count
    cnt = Counter()
    for p in corpus:
        for ch in p:
            if ch.isalpha():
                cnt[ch] += 1
    return cnt

class PuzzleSolverAI:
    """
    Heuristic solver that ranks candidate phrases matching the visible pattern.
    """

    def __init__(self, puzzles_file="data/bonus_puzzles.txt"):
        self.puzzles_file = puzzles_file
        self.corpus = _load_candidates(self.puzzles_file)
        self.letter_freq = _letter_frequency(self.corpus)
        # small smoothing constant
        self.total_letters = sum(self.letter_freq.values()) or 1

    def _score_candidate(self, pattern_str, candidate):
        """
        Score takes into account:
        - number of unknown (blanks) left (fewer is better)
        - letter frequency for filled letters (higher is better)
        - exact shape match (word lengths and spaces)
        - penalize length mismatch, but regex filters exact length so not necessary
        """
        score = 0.0

        # unknown count
        unknowns = sum(1 for p_ch, c_ch in zip(pattern_str, candidate) if p_ch == "_" and c_ch.isalpha())

        # reward filled letters that match high-frequency letters
        for p_ch, c_ch in zip(pattern_str, candidate):
            if p_ch == "_" and c_ch.isalpha():
                # higher frequency letters add more (log scaled)
                freq = self.letter_freq.get(c_ch, 0) + 1
                score += log(freq)

            elif p_ch == c_ch:
                # revealed letter confirming candidate -> add small positive
                score += 0.5

        # fewer unknowns -> higher score
        score -= unknowns * 1.2

        # word-shape bonus: number of words matching word lengths exactly
        pattern_words = pattern_str.split(" ")
        cand_words = candidate.split(" ")
        if len(pattern_words) == len(cand_words):
            shape_bonus = 0
            for pw, cw in zip(pattern_words, cand_words):
                if len(pw) == len(cw):
                    shape_bonus += 0.3
            score += shape_bonus

        # length penalty for too long/short (rare; regex filtered lengths usually)
        length_diff = abs(len(pattern_str) - len(candidate))
        score -= length_diff * 0.05

        return score

    def solve(self, pattern, candidates=None, top_n=5):
        """
        Return top_n candidate guesses (sorted by score).
        pattern: list or string with underscores for unknowns
        candidates: optional list to search
        """
        pattern_str = _normalize_pattern(pattern)
        if candidates is None:
            candidates = self.corpus

        regex = _pattern_to_regex(pattern_str)

        matched = [c for c in candidates if regex.match(c)]
        if not matched:
            # fallback: allow candidates with same number of words and lengths
            pw_lengths = [len(w) for w in pattern_str.split(" ")]
            def shape_ok(cand):
                parts = cand.split(" ")
                if len(parts) != len(pw_lengths):
                    return False
                return all(len(p) == l for p, l in zip(parts, pw_lengths))
            matched = [c for c in candidates if shape_ok(c)]

        scored = [(c, self._score_candidate(pattern_str, c)) for c in matched]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored[:top_n]]
