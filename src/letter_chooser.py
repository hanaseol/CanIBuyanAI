# src/letter_chooser.py
from collections import Counter
import re
from pathlib import Path

FREE_LETTERS = set("RSTLNE")
VOWELS = set("AEIOU")
CONSONANTS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") - VOWELS

def _normalize_pattern(pattern):
    """
    Accept pattern as list (['C','_',' ']) or string ("C _ _") and
    return a string with spaces preserved, uppercase, and '_' for blanks.
    """
    if isinstance(pattern, list):
        return "".join(pattern).upper()
    s = str(pattern).upper()
    # allow user to pass patterns like "C _ _  A"
    s = re.sub(r"[^A-Z _]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    # ensure blanks are underscores
    s = s.replace(" ", " ")
    return s

def _load_candidates(puzzles_file="data/bonus_puzzles.txt"):
    p = Path(puzzles_file)
    if not p.exists():
        return []
    return [line.strip().upper() for line in p.read_text().splitlines() if line.strip()]

def _pattern_to_regex_str(pattern_str):
    """
    Convert pattern string (with spaces and letters/_ characters) into a regex
    that matches the full phrase (space positions preserved).
    We'll convert spaces to literal spaces and underscores to '.' (single char).
    Example: 'C _ T  _ A _' -> '^C. T .A.$' but simpler approach below.
    """
    parts = []
    for ch in pattern_str:
        if ch == " ":
            parts.append(r"\s")
        elif ch == "_":
            parts.append(".")
        else:
            parts.append(re.escape(ch))
    regex = "^" + "".join(parts) + "$"
    # replace \s with actual space to ensure we match single space between words
    regex = regex.replace(r"\s", " ")
    return regex

class LetterChooserAI:
    """
    Heuristic letter chooser for the Wheel of Fortune bonus round.

    Usage:
        lc = LetterChooserAI()
        picks = lc.choose_letters(pattern, candidates=None)
        -> returns a 4-letter string, e.g. "BCD O" (no spaces actually "BCDO")
    """

    def __init__(self, puzzles_file="data/bonus_puzzles.txt"):
        self.puzzles_file = puzzles_file

    def choose_letters(self, pattern, candidates=None):
        """
        Choose 3 consonants + 1 vowel using frequency within remaining candidates.

        pattern: list or string pattern (letters, underscores, and spaces)
        candidates: optional list of candidate phrases to restrict to; if None, load from file.
        """
        pattern_str = _normalize_pattern(pattern)
        if candidates is None:
            candidates = _load_candidates(self.puzzles_file)

        # Build regex to filter candidates that match the visible letters and word lengths
        regex = re.compile(_pattern_to_regex_str(pattern_str))

        # Filter candidate pool
        filtered = [c for c in candidates if regex.match(c)]
        if not filtered:
            # fallback to unfiltered corpus
            filtered = candidates[:]

        # Count letters in *unrevealed* positions
        counts = Counter()
        for phrase in filtered:
            # iterate aligned with pattern (both have spaces in same positions ideally)
            # If lengths differ, skip phrase
            if len(phrase) != len(pattern_str):
                continue
            for p_ch, s_ch in zip(pattern_str, phrase):
                if p_ch == "_":
                    counts[s_ch] += 1

        # Remove free letters and already revealed
        revealed = set([ch for ch in pattern_str if ch.isalpha()])
        for fl in FREE_LETTERS | revealed:
            if fl in counts:
                del counts[fl]

        # Choose vowel with highest count among vowels
        vowel_counts = {v: counts.get(v, 0) for v in VOWELS}
        # If all zero, fallback to common vowel order
        if all(vv == 0 for vv in vowel_counts.values()):
            vowel_pick = "A"  # default fallback
        else:
            vowel_pick = max(vowel_counts.items(), key=lambda x: (x[1], x[0]))[0]

        # Choose top 3 consonants
        consonant_counts = {c: counts.get(c, 0) for c in CONSONANTS}
        # Fallback: global english-ish consonant order if all zero
        if all(v == 0 for v in consonant_counts.values()):
            fallback_order = list("TNSRLCDMGHPBVKXQJZ")  # rough English order
            cons_picks = [c for c in fallback_order if c not in FREE_LETTERS and c not in revealed][:3]
        else:
            # sort by count then alphabetically
            cons_picks = sorted(consonant_counts.items(), key=lambda x: (-x[1], x[0]))
            cons_picks = [c for c, _ in cons_picks][:3]

        picks = "".join(cons_picks) + vowel_pick
        return picks
