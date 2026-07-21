# -*- coding: utf-8 -*-
"""
Vocal Arena Automated Test Suite.
Provides rigorous unit tests for DatabaseManager, PronunciationEngine,
AICoach, PhoneticDictionary, and VocalAnalyticsReport.
"""

import os
import unittest
from datetime import datetime, timedelta

from database_manager import DatabaseManager
from pronunciation_engine import PronunciationEngine
from phonetic_dictionary import PhoneticDictionary
from vocal_analytics_report import VocalAnalyticsReport
from speech_therapy_drills import SpeechTherapyEngine
from speech_profile_db import SpeechProfileTracker

class TestDatabaseManager(unittest.TestCase):
    """Unit tests for the DatabaseManager JSON persistence engine."""

    def setUp(self):
        self.test_db_path = os.path.join(os.getcwd(), "data", "test_db.json")
        # Ensure clean slate
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = DatabaseManager(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_initial_db_creation(self):
        """Verifies that the database initializes with starter content if empty."""
        data = self.db.read_all()
        self.assertIn("tongueTwisters", data)
        self.assertIn("practiceAttempts", data)
        self.assertTrue(len(data["tongueTwisters"]) > 0)

    def test_add_tongue_twister(self):
        """Tests adding a new tongue twister to the catalog."""
        new_tw = {
            "id": "test-123",
            "text": "Red lorry yellow lorry",
            "language": "English",
            "difficulty": "easy",
            "category": "Classic",
            "focusSound": "L / R",
            "meaning": "Vocal focus on Ls and Rs.",
            "likes": 0,
            "attemptCount": 0
        }
        success = self.db.add_tongue_twister(new_tw)
        self.assertTrue(success)
        
        # Verify it was written and is queryable
        twisters = self.db.get_tongue_twisters(query="lorry")
        self.assertEqual(len(twisters), 1)
        self.assertEqual(twisters[0]["text"], "Red lorry yellow lorry")

    def test_increment_likes(self):
        """Verifies that like counters increment correctly."""
        twisters = self.db.get_tongue_twisters()
        target_id = twisters[0]["id"]
        original_likes = twisters[0].get("likes", 0)

        new_likes = self.db.increment_likes(target_id)
        self.assertEqual(new_likes, original_likes + 1)


class TestPronunciationEngine(unittest.TestCase):
    """Unit tests for speech velocity (WPM) and word alignment calculations."""

    def test_perfect_alignment(self):
        """Checks alignment with exact spoken matches."""
        target = "She sells seashells by the seashore"
        spoken = "She sells seashells by the seashore"
        alignment, accuracy = PronunciationEngine.calculate_alignment(target, spoken)
        
        self.assertEqual(accuracy, 100)
        self.assertEqual(len(alignment), 6)
        for word in alignment:
            self.assertEqual(word["status"], "correct")

    def test_skipped_word_alignment(self):
        """Checks alignment when words are skipped."""
        target = "Peter Piper picked a peck"
        spoken = "Peter picked a peck" # missed 'Piper'
        alignment, accuracy = PronunciationEngine.calculate_alignment(target, spoken)
        
        self.assertTrue(accuracy < 100)
        missed = [w for w in alignment if w["status"] == "missed"]
        self.assertEqual(len(missed), 1)
        self.assertEqual(missed[0]["targetWord"], "Piper")

    def test_extra_word_alignment(self):
        """Checks alignment when additional words are spoken."""
        target = "How much wood"
        spoken = "How much more wood" # extra 'more'
        alignment, accuracy = PronunciationEngine.calculate_alignment(target, spoken)
        
        self.assertEqual(accuracy, 100)
        extra = [w for w in alignment if w["status"] == "extra"]
        self.assertEqual(len(extra), 1)
        self.assertEqual(extra[0]["spokenWord"], "more")

    def test_wpm_calculation(self):
        """Checks word-velocity speed metrics calculation."""
        # 10 words in 5 seconds (5000 ms) = 120 WPM
        spoken = "one two three four five six seven eight nine ten"
        wpm = PronunciationEngine.calculate_wpm(spoken, 5000)
        self.assertEqual(wpm, 120)


class TestPhoneticDictionary(unittest.TestCase):
    """Unit tests for the custom IPA phonetic engine."""

    def test_ipa_lookup_known(self):
        """Checks that registered words lookup their exact IPA transcriptions."""
        self.assertEqual(PhoneticDictionary.get_ipa("peter"), "ˈpiːtər")
        self.assertEqual(PhoneticDictionary.get_ipa("seashells"), "ˈsiːˌʃelz")

    def test_ipa_lookup_unknown_heuristic(self):
        """Checks that unregistered words return a sound guess."""
        guess = PhoneticDictionary.get_ipa("shadow")
        self.assertIn("ʃ", guess) # 'sh' replacement rule

    def test_phonetic_distance(self):
        """Checks distance algorithm on IPA sound representation layers."""
        # 'peter' vs 'piper' share similar stops and liquids, should have moderate similarity
        dist = PhoneticDictionary.calculate_phonetic_distance("peter", "piper")
        self.assertTrue(0.0 < dist < 1.0)
        
        # Identical words must have 0.0 distance
        self.assertEqual(PhoneticDictionary.calculate_phonetic_distance("peter", "peter"), 0.0)

    def test_phonetic_collisions(self):
        """Checks that consonant clusters are identified inside tongue twisters."""
        collisions = PhoneticDictionary.analyze_phonetic_collisions("She sells seashells")
        # Should have sibilants as highly active sound group
        sibilant_count = next((count for group, count in collisions if group == "sibilants"), 0)
        self.assertTrue(sibilant_count > 0)


class TestVocalAnalyticsReport(unittest.TestCase):
    """Unit tests for computed user practice statistics and streaks."""

    def test_streak_calculation(self):
        """Checks daily streak accumulation increments consecutively."""
        twisters = [{"id": "tw-1", "focusSound": "S"}]
        
        today_iso = datetime.utcnow().isoformat() + "Z"
        yesterday_iso = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        day_before_iso = (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z"

        attempts = [
            {"twisterId": "tw-1", "timestamp": today_iso, "accuracy": 95, "wpm": 100},
            {"twisterId": "tw-1", "timestamp": yesterday_iso, "accuracy": 90, "wpm": 95},
            {"twisterId": "tw-1", "timestamp": day_before_iso, "accuracy": 88, "wpm": 90}
        ]

        reporter = VocalAnalyticsReport(attempts, twisters)
        self.assertEqual(reporter.compute_streaks(), 3)

    def test_vocal_stats_computation(self):
        """Checks rolling averages and variances."""
        twisters = [{"id": "tw-1", "focusSound": "S"}]
        attempts = [
            {"twisterId": "tw-1", "accuracy": 100, "wpm": 100},
            {"twisterId": "tw-1", "accuracy": 80, "wpm": 80}
        ]
        reporter = VocalAnalyticsReport(attempts, twisters)
        stats = reporter.get_vocal_stats()
        
        self.assertEqual(stats["totalAttempts"], 2)
        self.assertEqual(stats["avgAccuracy"], 90.0)
        self.assertEqual(stats["avgWpm"], 90.0)
        self.assertEqual(stats["maxAccuracy"], 100)


class TestSpeechTherapyEngine(unittest.TestCase):
    """Unit tests for vocal therapy and warmup drill engines."""

    def test_get_warmups(self):
        """Verifies that all standard physical warm-ups are loaded."""
        warmups = SpeechTherapyEngine.get_warmups()
        self.assertTrue(len(warmups) >= 4)
        self.assertEqual(warmups[0]["id"], "warmup-lip-flutter")

    def test_assemble_therapy_routine(self):
        """Checks routine builder compiles correct prescribed warm-ups and drills."""
        routine = SpeechTherapyEngine.assemble_therapy_routine("S")
        self.assertEqual(routine["targetPhoneme"], "S")
        self.assertTrue(len(routine["neuromuscularDrills"]) > 0)


class TestSpeechProfileTracker(unittest.TestCase):
    """Unit tests for phonetic muscle modeling and resonance profiling."""

    def test_compile_speech_profile(self):
        """Checks profile compiles clean indicators and physiological suggestions."""
        attempts = [
            {"accuracy": 95, "wpm": 110},
            {"accuracy": 88, "wpm": 90}
        ]
        tracker = SpeechProfileTracker(attempts)
        profile = tracker.compile_speech_profile()
        
        self.assertTrue(profile["vowelSpaceIndex"] > 1.0)
        self.assertTrue(profile["motorControlScore"] > 50.0)
        self.assertTrue(len(profile["coachingAdvice"]) > 0)


if __name__ == "__main__":
    unittest.main()
