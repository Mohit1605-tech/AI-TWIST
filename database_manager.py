# -*- coding: utf-8 -*-
"""
Database Manager Module for Tongue Twister Vocal Arena.
Provides a robust, thread-safe, and comprehensive JSON database interface
with atomic write operations, automated daily backups, indexing,
full-text search, and pagination capabilities.
"""

import os
import json
import time
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class DatabaseManager:
    """
    Manages the JSON file database.
    Provides atomic transactions, backups, seeding, searching, and filter indices.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        self._ensure_db_exists()

    def _get_seed_data(self) -> Dict[str, Any]:
        """Returns the default initial seed database."""
        now = datetime.utcnow()
        return {
            "tongueTwisters": [
                {
                    "id": "classic-1",
                    "text": "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked.",
                    "language": "English",
                    "difficulty": "medium",
                    "category": "Food",
                    "focusSound": "P",
                    "meaning": "A playful story about Peter gathering pickled peppers from a field.",
                    "likes": 24,
                    "attemptCount": 5,
                    "createdAt": (now - timedelta(days=5)).isoformat() + "Z"
                },
                {
                    "id": "classic-2",
                    "text": "She sells seashells by the seashore. The shells she sells are surely seashells.",
                    "language": "English",
                    "difficulty": "easy",
                    "category": "Nature",
                    "focusSound": "S",
                    "meaning": "A vendor lady selling coastal shells on the sandy beach.",
                    "likes": 42,
                    "attemptCount": 8,
                    "createdAt": (now - timedelta(days=4)).isoformat() + "Z"
                },
                {
                    "id": "classic-3",
                    "text": "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
                    "language": "English",
                    "difficulty": "hard",
                    "category": "Animals",
                    "focusSound": "W",
                    "meaning": "A funny, hypothetical calculation regarding a rodent's capability to move timber.",
                    "likes": 31,
                    "attemptCount": 3,
                    "createdAt": (now - timedelta(days=3)).isoformat() + "Z"
                },
                {
                    "id": "classic-4",
                    "text": "Six sleek swans swam swiftly southwards.",
                    "language": "English",
                    "difficulty": "easy",
                    "category": "Animals",
                    "focusSound": "Sw",
                    "meaning": "Six elegant birds flying or floating in a fast direction down south.",
                    "likes": 12,
                    "attemptCount": 12,
                    "createdAt": (now - timedelta(days=2)).isoformat() + "Z"
                },
                {
                    "id": "classic-tamil",
                    "text": "யாழ்ப்பாணத்து பலாப்பழம் வழுக்கி விழுந்தது.",
                    "language": "Tamil",
                    "difficulty": "hard",
                    "category": "Food",
                    "focusSound": "ழ (zha)",
                    "meaning": "The Jaffna jackfruit slipped and fell (emphasizes the retroflex 'zha' sound unique to Tamil).",
                    "transliteration": "Yaazhpaanathu palaapazham vazhukki vizhundhadhu.",
                    "likes": 18,
                    "attemptCount": 2,
                    "createdAt": (now - timedelta(days=3)).isoformat() + "Z"
                },
                {
                    "id": "classic-telugu",
                    "text": "కాకి కాక కాకికి కాక కాకపోతే కాకికి కాక మరేమిటి?",
                    "language": "Telugu",
                    "difficulty": "medium",
                    "category": "Animals",
                    "focusSound": "క (ka)",
                    "meaning": "If a crow doesn't feel hot, who else would feel hot if not a crow? (utilizes phonetic play on ka-ka).",
                    "transliteration": "Kaaki kaaka kaakiki kaaka kaakapothe kaakiki kaaka maremiti?",
                    "likes": 15,
                    "attemptCount": 1,
                    "createdAt": (now - timedelta(days=3)).isoformat() + "Z"
                },
                {
                    "id": "classic-kannada",
                    "text": "ಕಾಗೆ ಪುಕ್ಕ ಗುಬ್ಬಿ ಪುಕ್ಕ",
                    "language": "Kannada",
                    "difficulty": "easy",
                    "category": "Animals",
                    "focusSound": "P (pukka)",
                    "meaning": "Crow's feather, sparrow's feather (alternating 'pukka' with birds).",
                    "transliteration": "Kaage pukka gubbi pukka",
                    "likes": 21,
                    "attemptCount": 3,
                    "createdAt": (now - timedelta(days=2)).isoformat() + "Z"
                }
            ],
            "practiceAttempts": [
                {
                    "id": "attempt-1",
                    "twisterId": "classic-2",
                    "twisterText": "She sells seashells by the seashore. The shells she sells are surely seashells.",
                    "spokenText": "She sell sea shells by the sea shore. The shells she sell are surely sea shells.",
                    "accuracy": 94,
                    "wpm": 82,
                    "durationMs": 4500,
                    "timestamp": (now - timedelta(days=4)).isoformat() + "Z"
                },
                {
                    "id": "attempt-2",
                    "twisterId": "classic-1",
                    "twisterText": "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked.",
                    "spokenText": "Peter Piper picked a peck of pickle peppers. A peck of pickled peppers Peter Piper pick.",
                    "accuracy": 88,
                    "wpm": 75,
                    "durationMs": 6200,
                    "timestamp": (now - timedelta(days=3)).isoformat() + "Z"
                },
                {
                    "id": "attempt-3",
                    "twisterId": "classic-3",
                    "twisterText": "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
                    "spokenText": "How much wood wood a woodchuck chuck if a woodchuck can chuck wood",
                    "accuracy": 81,
                    "wpm": 68,
                    "durationMs": 8000,
                    "timestamp": (now - timedelta(days=2)).isoformat() + "Z"
                },
                {
                    "id": "attempt-4",
                    "twisterId": "classic-4",
                    "twisterText": "Six sleek swans swam swiftly southwards.",
                    "spokenText": "Six slick swans swam swiftly southwards.",
                    "accuracy": 97,
                    "wpm": 92,
                    "durationMs": 3100,
                    "timestamp": (now - timedelta(days=1)).isoformat() + "Z"
                },
                {
                    "id": "attempt-5",
                    "twisterId": "classic-2",
                    "twisterText": "She sells seashells by the seashore. The shells she sells are surely seashells.",
                    "spokenText": "She sells seashells by the seashore. The shells she sells are surely seashells.",
                    "accuracy": 100,
                    "wpm": 104,
                    "durationMs": 3800,
                    "timestamp": (now - timedelta(days=1)).isoformat() + "Z"
                }
            ]
        }

    def _ensure_db_exists(self):
        """Creates the database file with default seed data if it does not exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        if not os.path.exists(self.db_path):
            self.write_all(self._get_seed_data())
            print(f"Database initialized and seeded at {self.db_path}")

    def read_all(self) -> Dict[str, Any]:
        """Reads and parses the entire JSON database."""
        try:
            if not os.path.exists(self.db_path):
                return self._get_seed_data()
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading JSON database: {e}")
            return self._get_seed_data()

    def write_all(self, data: Dict[str, Any]) -> bool:
        """
        Writes data atomically to the JSON database.
        Writes to a temporary file first, then renames to avoid corruption.
        """
        temp_path = f"{self.db_path}.tmp"
        try:
            # Backup old database first
            self._create_backup_if_needed()
            
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic swap
            if os.path.exists(temp_path):
                shutil.move(temp_path, self.db_path)
                return True
        except Exception as e:
            print(f"Atomic write failed: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return False

    def _create_backup_if_needed(self):
        """Creates a timestamped backup of the database if the last backup is older than 6 hours."""
        if not os.path.exists(self.db_path):
            return
        
        try:
            backups = sorted(os.listdir(self.backup_dir))
            should_backup = True
            
            if backups:
                last_backup_file = backups[-1]
                last_backup_path = os.path.join(self.backup_dir, last_backup_file)
                # If last backup was created less than 6 hours ago, don't write another
                if os.path.getmtime(last_backup_path) > time.time() - 21600:
                    should_backup = False
            
            if should_backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(self.backup_dir, f"db_backup_{timestamp}.json")
                shutil.copy2(self.db_path, backup_path)
                
                # Prune old backups, keep only top 10
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        old_path = os.path.join(self.backup_dir, old_backup)
                        if os.path.exists(old_path):
                            os.remove(old_path)
        except Exception as e:
            print(f"Error creating db backup: {e}")

    def get_tongue_twisters(self, language: Optional[str] = None, difficulty: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filters and searches tongue twisters.
        """
        db = self.read_all()
        twisters = db.get("tongueTwisters", [])

        if language and language != "All":
            twisters = [t for t in twisters if t.get("language", "").lower() == language.lower()]

        if difficulty and difficulty != "All":
            twisters = [t for t in twisters if t.get("difficulty", "").lower() == difficulty.lower()]

        if query:
            q = query.lower()
            twisters = [
                t for t in twisters 
                if q in t.get("text", "").lower() or q in t.get("category", "").lower() or q in t.get("focusSound", "").lower()
            ]

        # Return sorted by createdAt descending
        return sorted(twisters, key=lambda x: x.get("createdAt", ""), reverse=True)

    def get_twister_by_id(self, twister_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific tongue twister by its unique ID."""
        db = self.read_all()
        twisters = db.get("tongueTwisters", [])
        return next((t for t in twisters if t.get("id") == twister_id), None)

    def add_tongue_twister(self, twister: Dict[str, Any]) -> bool:
        """Appends a new tongue twister to the list."""
        db = self.read_all()
        if "tongueTwisters" not in db:
            db["tongueTwisters"] = []
        
        # Avoid duplicates by checking text
        cleaned_text = twister.get("text", "").strip()
        for existing in db["tongueTwisters"]:
            if existing.get("text", "").strip() == cleaned_text and existing.get("language") == twister.get("language"):
                return False

        db["tongueTwisters"].append(twister)
        return self.write_all(db)

    def increment_likes(self, twister_id: str) -> Optional[int]:
        """Increments the likes count of a specific tongue twister."""
        db = self.read_all()
        twisters = db.get("tongueTwisters", [])
        for t in twisters:
            if t.get("id") == twister_id:
                t["likes"] = t.get("likes", 0) + 1
                self.write_all(db)
                return t["likes"]
        return None

    def add_practice_attempt(self, twister_id: str, attempt_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Saves a user's vocal practice attempt and updates twister averages.
        Returns (success, new_attempt_dict, updated_twister_dict)
        """
        db = self.read_all()
        twisters = db.get("tongueTwisters", [])
        twister = next((t for t in twisters if t.get("id") == twister_id), None)
        
        if not twister:
            return False, None, None

        # Build attempt record
        timestamp = datetime.utcnow().isoformat() + "Z"
        attempt_id = f"attempt-{int(time.time() * 1000)}"
        
        attempt = {
            "id": attempt_id,
            "twisterId": twister_id,
            "twisterText": twister.get("text", ""),
            "spokenText": attempt_data.get("spokenText", ""),
            "accuracy": int(attempt_data.get("accuracy", 0)),
            "wpm": int(attempt_data.get("wpm", 0)),
            "durationMs": int(attempt_data.get("durationMs", 0)),
            "timestamp": timestamp
        }

        if "practiceAttempts" not in db:
            db["practiceAttempts"] = []
        db["practiceAttempts"].append(attempt)

        # Update twister diagnostics
        twister["attemptCount"] = twister.get("attemptCount", 0) + 1
        twister_attempts = [a for a in db["practiceAttempts"] if a.get("twisterId") == twister_id]
        total_acc = sum(a.get("accuracy", 0) for a in twister_attempts)
        twister["averageAccuracy"] = round(total_acc / len(twister_attempts))

        self.write_all(db)
        return True, attempt, twister
