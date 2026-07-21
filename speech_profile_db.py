# -*- coding: utf-8 -*-
"""
User Speech Profile and Resonance Tracker.
Models physiological parameters (jaw drop, vowel opening space, lip contraction)
based on historical practice logs, providing an adaptive speech profile.
"""

from typing import Dict, List, Any

class SpeechProfileTracker:
    """
    Tracks and models vocal physiological metrics from historical scores.
    Recommends physical adjustments to lips, tongue, or jaw.
    """

    def __init__(self, attempts: List[Dict[str, Any]]):
        self.attempts = attempts

    def calculate_vowel_space_index(self) -> float:
        """
        Calculates a simulated Vowel Space Index (VSI) based on vocal scores.
        High accuracy on vowel-heavy twisters correlates to optimal articulation spacing.
        """
        if not self.attempts:
            return 1.0 # Baseline scale

        total_accuracy = sum(a.get("accuracy", 0) for a in self.attempts)
        avg_acc = total_accuracy / len(self.attempts)
        
        # Scale VSI between 0.8 (muffled) and 1.5 (extremely clear formants)
        vsi = 0.8 + (avg_acc / 100.0) * 0.7
        return round(vsi, 2)

    def evaluate_motor_control_score(self) -> float:
        """
        Measures motor speed-consistency.
        Higher WPM with high accuracy translates to optimal neuromuscular speech control.
        """
        if not self.attempts:
            return 50.0 # Mid baseline

        total_acc = 0.0
        total_wpm = 0.0
        count = 0

        for a in self.attempts:
            acc = a.get("accuracy", 0)
            wpm = a.get("wpm", 0)
            if acc >= 80: # Only count solid attempts
                total_acc += acc
                total_wpm += wpm
                count += 1

        if count == 0:
            return 35.0 # Slurred / slow baseline

        avg_acc = total_acc / count
        avg_wpm = total_wpm / count

        # Motor control formula combining speed and accuracy
        control_score = (avg_acc * 0.6) + (min(150.0, avg_wpm) * 0.4)
        return round(min(100.0, control_score), 1)

    def get_physiological_advice(self) -> List[str]:
        """
        Generates targeted physiological advice for physical muscle adjustments
        based on the user's motor control and vowel space indices.
        """
        vsi = self.calculate_vowel_space_index()
        motor = self.evaluate_motor_control_score()
        advice = []

        if vsi < 1.1:
            advice.append("Vowel Aperture Alert: Focus on dropping your lower lower jaw wider for vowels (e.g. 'ah', 'ee', 'oh'). This expands your oral resonance space.")
        else:
            advice.append("Formant Precision: Your vowel acoustic formants are highly defined. Keep your current vertical jaw aperture stable.")

        if motor < 65.0:
            advice.append("Syllabic Lag: Your speech muscles are tensing up on rapid phoneme alternates. Spend 30 seconds humming or lip-fluttering to relax your soft palate.")
        else:
            advice.append("Supersonic Coordination: Your tongue muscles are snapping cleanly between plosives and sibilants. Ready for faster pacing.")

        return advice

    def compile_speech_profile(self) -> Dict[str, Any]:
        """Compiles physiological indicators into a unified diagnostic card."""
        return {
            "vowelSpaceIndex": self.calculate_vowel_space_index(),
            "motorControlScore": self.evaluate_motor_control_score(),
            "coachingAdvice": self.get_physiological_advice()
        }
