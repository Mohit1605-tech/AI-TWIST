# -*- coding: utf-8 -*-
"""
Vocal Analytics Report Module.
Aggregates session logs to compute performance indicators including rolling averages,
accuracy variances, peak word-velocity rates, daily streak counts,
and phonetic weaknesses. Generates structured, readable analytical reports.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Tuple, Optional

class VocalAnalyticsReport:
    """
    Performs data science on practice attempt logs.
    Computes streaks, variances, and formats clean reports of vocal progress.
    """

    def __init__(self, attempts: List[Dict[str, Any]], twisters: List[Dict[str, Any]]):
        self.attempts = attempts
        self.twisters = {t["id"]: t for t in twisters}

    def compute_streaks(self) -> int:
        """
        Calculates the consecutive daily practice streak.
        A streak increments if attempts exist on consecutive calendar days.
        """
        if not self.attempts:
            return 0

        dates_practiced = set()
        for a in self.attempts:
            timestamp_str = a.get("timestamp")
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    dates_practiced.add(dt.date())
                except Exception:
                    pass

        sorted_dates = sorted(list(dates_practiced), reverse=True)
        if not sorted_dates:
            return 0

        today = date.today()
        # If the user hasn't practiced today or yesterday, the streak is broken (0)
        if sorted_dates[0] < today - timedelta(days=1):
            return 0

        streak = 1
        for i in range(len(sorted_dates) - 1):
            delta = sorted_dates[i] - sorted_dates[i+1]
            if delta.days == 1:
                streak += 1
            elif delta.days > 1:
                break # Streak interrupted

        return streak

    def get_vocal_stats(self) -> Dict[str, Any]:
        """
        Computes detailed descriptive statistics of accuracy and speed (WPM).
        """
        if not self.attempts:
            return {
                "totalAttempts": 0, "avgAccuracy": 0.0, "maxAccuracy": 0,
                "avgWpm": 0.0, "maxWpm": 0, "varianceAccuracy": 0.0
            }

        accuracies = [a.get("accuracy", 0) for a in self.attempts]
        wpms = [a.get("wpm", 0) for a in self.attempts]

        avg_acc = sum(accuracies) / len(accuracies)
        avg_wpm = sum(wpms) / len(wpms)

        # Calculate variance of accuracy to understand consistency
        mean_acc = sum(accuracies) / len(accuracies)
        var_acc = sum((x - mean_acc) ** 2 for x in accuracies) / len(accuracies) if len(accuracies) > 1 else 0.0

        return {
            "totalAttempts": len(self.attempts),
            "avgAccuracy": round(avg_acc, 1),
            "maxAccuracy": max(accuracies),
            "avgWpm": round(avg_wpm, 1),
            "maxWpm": max(wpms),
            "varianceAccuracy": round(var_acc, 2)
        }

    def identify_phonetic_weakness(self) -> Tuple[str, float]:
        """
        Correlates practice accuracy with tongue-twister focus sounds
        to locate the phonetic sounds (phonemes) giving the user the most difficulty.
        Returns a tuple of (hardest_sound, average_accuracy_on_sound).
        """
        if not self.attempts:
            return "None", 100.0

        sound_scores = {}
        for a in self.attempts:
            tw_id = a.get("twisterId")
            tw = self.twisters.get(tw_id)
            if tw:
                sound = tw.get("focusSound", "Generic").upper()
                acc = a.get("accuracy", 0)
                if sound not in sound_scores:
                    sound_scores[sound] = []
                sound_scores[sound].append(acc)

        if not sound_scores:
            return "None", 100.0

        # Calculate average score per sound
        sound_averages = {
            sound: sum(scores) / len(scores)
            for sound, scores in sound_scores.items()
        }

        # Find the sound with the lowest average accuracy score
        hardest = min(sound_averages, key=sound_averages.get)
        return hardest, round(sound_averages[hardest], 1)

    def generate_analytical_report(self) -> str:
        """
        Formats a beautifully detailed statistical markdown text report
        outlining vocal metrics, consistency assessments, and phonetic diagnostics.
        """
        stats = self.get_vocal_stats()
        streak = self.compute_streaks()
        weak_sound, weak_acc = self.identify_phonetic_weakness()

        if stats["totalAttempts"] == 0:
            return (
                "# Articulation Progress Analytics\n\n"
                "No practice attempts have been logged yet. "
                "Go to the **Vocal Arena**, pick a tongue twister, click the mic, and record your voice to generate your report!"
            )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine consistency level based on accuracy variance
        var = stats["varianceAccuracy"]
        if var < 15:
            consistency = "Supersonic (Extremely stable pronunciation patterns)"
        elif var < 50:
            consistency = "Moderate (Refined control with minor speech slips)"
        else:
            consistency = "Fluctuating (Highly variable articulation - needs steady breathing exercises)"

        report = (
            f"# VOCAL ARENA DIAGNOSTIC REPORT\n"
            f"Generated: {now_str}\n"
            f"=========================================\n\n"
            f"## 📊 CORE PERFORMANCE METRICS\n"
            f"- **Total Practice Sessions**: {stats['totalAttempts']} logs\n"
            f"- **Average Articulation Accuracy**: {stats['avgAccuracy']}%\n"
            f"- **Peak Articulation Accuracy**: {stats['maxAccuracy']}%\n"
            f"- **Average Speech Tempo**: {stats['avgWpm']} words/min\n"
            f"- **Peak Speech Tempo**: {stats['maxWpm']} words/min\n"
            f"- **Active Practice Streak**: {streak} consecutive days\n\n"
            f"## 🎯 PHONETIC & ACOUSTIC ANALYSIS\n"
            f"- **Critical Phonetic Sound Block**: /{weak_sound}/ sound groups\n"
            f"  *The average accuracy on this letter is {weak_acc}%. Practicing more /{weak_sound}/ tongue twisters is recommended to smooth articulation transition boundaries.*\n"
            f"- **Speech Consistency Level**: {consistency} (Variance: {var})\n\n"
            f"## 💡 PERSONAL COACHING RECOMMENDATION\n"
        )

        if stats["avgAccuracy"] >= 90:
            report += (
                "Your vocal articulation is top-tier! You have mastered oral posture and breath coordination. "
                "To push boundaries, challenge yourself with 'Jaw Breaker' (Hard) tongue twisters and attempt to increase your "
                "vocal speed beyond 110 WPM without dropping accuracy. Try focusing on rapid plosives."
            )
        elif stats["avgAccuracy"] >= 75:
            report += (
                "You show strong speech capabilities with stable vocal tempo. Minor slips occur during "
                "complex phoneme shifts (like shifting rapidly between sibilants 's' and 'sh'). "
                "Ensure your jaw is completely relaxed. Do not rush; keep your current comfortable pace before pushing faster."
            )
        else:
            report += (
                "Vocal transitions are currently causing speech knots. This is entirely normal! "
                "We strongly recommend working at a slow speed (below 65 WPM). Over-articulate every syllable, "
                "pronouncing starting consonants with a clean, sharp puff of air, and allow your muscle memory to settle."
            )

        return report
