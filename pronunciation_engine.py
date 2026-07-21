# -*- coding: utf-8 -*-
"""
Pronunciation Engine Module for Tongue Twister Vocal Arena.
Provides core algorithms for linguistic text normalization, Levenshtein distance,
and a Needleman-Wunsch inspired global sequence alignment to match a user's
spoken transcription against a target tongue twister with phonetic resilience.
"""

import re
from typing import Dict, List, Any, Tuple, Optional

class PronunciationEngine:
    """
    Algorithmic class for analyzing vocal accuracy on tongue twisters.
    Computes sequence alignment and labels each word with an articulation state.
    """

    @staticmethod
    def clean_word(word: str) -> str:
        """
        Removes punctuation, special characters, and normalizes unicode spacing
        to isolate the raw phonetic word for alignment and scoring.
        """
        if not word:
            return ""
        # Remove standard punctuation, keeping apostrophes for contractions (e.g. don't)
        cleaned = re.sub(r"[.,\/#!$%\^\x16&\*;:{}=\-_`~()?\"\[\]«»]", "", word.lower())
        return cleaned.strip()

    @classmethod
    def levenshtein_distance(cls, s1: str, s2: str) -> int:
        """
        Calculates the standard edit distance between two strings.
        Used to measure spelling similarity for phonetic matching.
        """
        if len(s1) < len(s2):
            return cls.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (0 if c1 == c2 else 1)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @classmethod
    def calculate_alignment(cls, target_text: str, spoken_text: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Performs sequence alignment of spoken text against the target twister.
        Uses Dynamic Programming to minimize the phonetic and edit distance mismatch cost.

        Match cost rules:
          - Cost 0: Perfect matching word
          - Cost 1: Partial match (e.g. substrings, closely related phonemes, or low Levenshtein edit distance ratio)
          - Cost 2: Complete mismatch (or deletion/insertion)
        """
        target_words = [w for w in target_text.split() if w]
        spoken_words = [w for w in spoken_text.split() if w]

        m = len(target_words)
        n = len(spoken_words)

        # DP cost matrix initiation
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Base case costs for boundary gaps (representing deletions/insertions)
        for i in range(m + 1):
            dp[i][0] = i * 2
        for j in range(n + 1):
            dp[0][j] = j * 2

        # Compute optimal edit graph path
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                t_w = cls.clean_word(target_words[i - 1])
                s_w = cls.clean_word(spoken_words[j - 1])

                match_cost = 2
                if t_w == s_w:
                    match_cost = 0
                elif len(t_w) >= 3 and len(s_w) >= 3 and (t_w in s_w or s_w in t_w):
                    match_cost = 1
                else:
                    dist = cls.levenshtein_distance(t_w, s_w)
                    max_len = max(len(t_w), len(s_w))
                    if max_len > 0 and (dist / max_len) < 0.45:
                        match_cost = 1

                dp[i][j] = min(
                    dp[i - 1][j - 1] + match_cost, # Diagonal path (Match or Substitution)
                    dp[i - 1][j] + 2,             # Upward path (Deletion of target word / Missed word)
                    dp[i][j - 1] + 2              # Leftward path (Insertion of spoken word / Extra word)
                )

        # Backtrack alignment path
        alignment = []
        i, j = m, n

        while i > 0 or j > 0:
            if i > 0 and j > 0:
                t_w = cls.clean_word(target_words[i - 1])
                s_w = cls.clean_word(spoken_words[j - 1])

                match_cost = 2
                if t_w == s_w:
                    match_cost = 0
                elif len(t_w) >= 3 and len(s_w) >= 3 and (t_w in s_w or s_w in t_w):
                    match_cost = 1
                else:
                    dist = cls.levenshtein_distance(t_w, s_w)
                    max_len = max(len(t_w), len(s_w))
                    if max_len > 0 and (dist / max_len) < 0.45:
                        match_cost = 1

                score_diagonal = dp[i - 1][j - 1] + match_cost
                score_up = dp[i - 1][j] + 2

                if dp[i][j] == score_diagonal:
                    alignment.insert(0, {
                        "targetWord": target_words[i - 1],
                        "spokenWord": spoken_words[j - 1],
                        "status": "correct" if match_cost == 0 else "partial"
                    })
                    i -= 1
                    j -= 1
                elif dp[i][j] == score_up:
                    alignment.insert(0, {
                        "targetWord": target_words[i - 1],
                        "spokenWord": None,
                        "status": "missed"
                    })
                    i -= 1
                else:
                    alignment.insert(0, {
                        "targetWord": "",
                        "spokenWord": spoken_words[j - 1],
                        "status": "extra"
                    })
                    j -= 1
            elif i > 0:
                alignment.insert(0, {
                    "targetWord": target_words[i - 1],
                    "spokenWord": None,
                    "status": "missed"
                })
                i -= 1
            else:
                alignment.insert(0, {
                    "targetWord": "",
                    "spokenWord": spoken_words[j - 1],
                    "status": "extra"
                })
                j -= 1

        # Calculate accuracy score based on the aligned items
        target_matches = [item for item in alignment if item["targetWord"] != ""]
        if not target_matches:
            return alignment, 0

        correct_count = sum(1 for item in target_matches if item["status"] == "correct")
        partial_count = sum(1 for item in target_matches if item["status"] == "partial")

        raw_score = ((correct_count + partial_count * 0.5) / len(target_words)) * 100
        accuracy = min(100, max(0, round(raw_score)))

        return alignment, accuracy

    @staticmethod
    def calculate_wpm(spoken_text: str, duration_ms: int) -> int:
        """
        Calculates user's speech velocity in Words Per Minute (WPM).
        Standardizes calculations to clamp values between logical speech rates.
        """
        if duration_ms <= 0:
            return 0
        words_count = len([w for w in spoken_text.split() if w])
        minutes = duration_ms / 60000.0
        calculated = round(words_count / minutes) if minutes > 0 else 0
        return min(250, max(10, calculated))
