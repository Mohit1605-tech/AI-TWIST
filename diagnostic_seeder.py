# -*- coding: utf-8 -*-
"""
Practice Log Simulator and Diagnostic Seeder.
Generates 100 realistic practice runs across a 30-day window with normal-distribution
learning curves (representing progressive improvement in speech accuracy and WPM metrics).
Useful for validating progress charts and reporting modules.
"""

import random
from datetime import datetime, timedelta
from database_manager import DatabaseManager

def seed_simulation_data(db_path: str = "data/db.json"):
    """
    Seeds the target database with 30 days of consecutive practice runs
    exhibiting a standard vocal training learning curve.
    """
    db = DatabaseManager(db_path)
    twisters = db.get_tongue_twisters()
    
    if not twisters:
        print("No target twisters found in database. Cannot simulate runs.")
        return

    # Clear old attempts to ensure a clean progress curve
    data = db.read_all()
    data["practiceAttempts"] = []
    db.write_all(data)

    base_date = datetime.utcnow() - timedelta(days=30)
    current_accuracy = 70.0 # Starts at 70%
    current_wpm = 85.0      # Starts at 85 WPM

    attempts_logged = 0

    for day in range(30):
        practice_date = base_date + timedelta(days=day)
        
        # Simulate 2 to 4 runs per day
        runs_today = random.randint(2, 4)
        for run in range(runs_today):
            twister = random.choice(twisters)
            
            # Learning curve: gradual improvements with random daily jitter
            improvement_factor = (day / 30.0)
            target_acc = min(99.0, current_accuracy + (improvement_factor * 20.0) + random.uniform(-5.0, 5.0))
            target_wpm = min(140.0, current_wpm + (improvement_factor * 40.0) + random.uniform(-10.0, 10.0))

            # Simulate duration in milliseconds (based on length and WPM)
            word_count = len(twister["text"].split())
            duration_ms = int((word_count / target_wpm) * 60.0 * 1000.0)

            # Generate spoken transcription with minor variations based on accuracy
            spoken_words = twister["text"].split()
            if target_acc < 85:
                # Mock a slurred/skipped word for lower accuracy
                swap_idx = random.randint(0, len(spoken_words) - 1)
                spoken_words[swap_idx] = "something" if random.random() > 0.5 else spoken_words[swap_idx][:-2]

            spoken_text = " ".join(spoken_words)
            timestamp_iso = (practice_date + timedelta(hours=random.randint(8, 20))).isoformat() + "Z"

            attempt = {
                "id": f"sim-attempt-{day}-{run}",
                "twisterId": twister["id"],
                "spokenText": spoken_text,
                "accuracy": round(target_acc, 1),
                "wpm": round(target_wpm, 1),
                "durationMs": duration_ms,
                "timestamp": timestamp_iso
            }

            db.add_practice_attempt(twister["id"], attempt)
            attempts_logged += 1

    print(f"Simulation completed! Logged {attempts_logged} practice runs across 30 days to database.")

if __name__ == "__main__":
    seed_simulation_data()
