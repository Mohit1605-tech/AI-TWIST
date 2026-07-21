# -*- coding: utf-8 -*-
"""
Speech Therapy and Neuromuscular Drills Module.
Provides structured speech-therapy warm-ups, muscle-coordination patterns,
and target-sound drills designed to release tongue/jaw tension and improve articulation.
"""

from typing import Dict, List, Any

# Define clinical-style vocal warmups
VOCAL_WARMUPS: List[Dict[str, Any]] = [
    {
        "id": "warmup-lip-flutter",
        "name": "Bilabial Lip Flutter",
        "focusSound": "P / B / M",
        "durationSeconds": 30,
        "instructions": "Inhale deeply, relax your lips, and blow air through them to create a motorboat sound ('brrr'). Keep the vibration steady.",
        "targetMuscles": "Orbicularis oris (lips), pulmonary lungs"
    },
    {
        "id": "warmup-tongue-trill",
        "name": "Alveolar Tongue Trills",
        "focusSound": "T / D / R",
        "durationSeconds": 45,
        "instructions": "Place the tip of your tongue loosely behind your upper front teeth. Exhale sharply, allowing the tongue tip to flutter in the airflow.",
        "targetMuscles": "Superior longitudinal muscle of the tongue"
    },
    {
        "id": "warmup-sibilant-hiss",
        "name": "Sibilant Airflow Hiss",
        "focusSound": "S / Z / SH",
        "durationSeconds": 30,
        "instructions": "Inhale, then slowly release a continuous, high-pitched hiss ('sssssss'). Focus on keeping the sound narrow and completely uniform.",
        "targetMuscles": "Transverse and vertical tongue muscles, abdominal wall"
    },
    {
        "id": "warmup-jaw-drop",
        "name": "Masseter Tension Release",
        "focusSound": "All",
        "durationSeconds": 60,
        "instructions": "Gently drop your lower jaw as far as comfortable. Slowly sweep your chin from left to right, then massage your cheek muscles.",
        "targetMuscles": "Masseter (jaw joint), temporalis"
    },
    {
        "id": "warmup-hum",
        "name": "Resonant Hum",
        "focusSound": "N / M / NG",
        "durationSeconds": 45,
        "instructions": "Keep your lips gently sealed and teeth slightly parted. Hum a comfortable tone, focusing on feeling the vibration in your nose and facial bones.",
        "targetMuscles": "Laryngeal muscles, velopharyngeal port"
    }
]

# Neuromuscular speech-therapy articulation drills grouped by target phonemes
ARTICULATION_DRILLS: Dict[str, List[str]] = {
    "sibilants": [
        "Sip, slip, snip, snap, snarl, slide.",
        "She sees seven shiny silver circles.",
        "The sharp sifted soot drifted swiftly south."
    ],
    "plosives": [
        "Pat, bat, tap, dab, pack, back, gap.",
        "Peter bought pretty pink blooming petunias.",
        "Tiny timid turtles travel toward tall trees."
    ],
    "liquids": [
        "Red lorry, yellow lorry, red lorry, yellow lorry.",
        "Larry ran randomly around the large lake.",
        "Willy's wild wheelbarrow wobbled wildly."
    ],
    "nasals": [
        "Many mice make merry morning music.",
        "Noisy newts nested near neat nutmeg trees.",
        "Singing ringing dinging clinging metal springs."
    ]
}

class SpeechTherapyEngine:
    """
    Manages speech therapy schedules, warm-up lists, and clinical
    drills based on specific phonetic challenges.
    """

    @classmethod
    def get_warmups(cls) -> List[Dict[str, Any]]:
        """Returns all registered warm-ups."""
        return VOCAL_WARMUPS

    @classmethod
    def get_drills_for_sound(cls, sound_category: str) -> List[str]:
        """
        Returns a set of motor-articulation drills targeted at a specific sound group.
        Default to general plosives if not matched.
        """
        sc_lower = sound_category.lower()
        if "s" in sc_lower or "sh" in sc_lower or "z" in sc_lower:
            return ARTICULATION_DRILLS["sibilants"]
        elif "p" in sc_lower or "b" in sc_lower or "t" in sc_lower or "d" in sc_lower or "k" in sc_lower:
            return ARTICULATION_DRILLS["plosives"]
        elif "l" in sc_lower or "r" in sc_lower or "w" in sc_lower:
            return ARTICULATION_DRILLS["liquids"]
        elif "m" in sc_lower or "n" in sc_lower or "ng" in sc_lower:
            return ARTICULATION_DRILLS["nasals"]
        else:
            return ARTICULATION_DRILLS["plosives"]

    @classmethod
    def assemble_therapy_routine(cls, target_phoneme: str) -> Dict[str, Any]:
        """
        Creates a custom 3-step physical therapy routine for correcting
        slurs on a specific target sound.
        """
        warmups = [w for w in VOCAL_WARMUPS if target_phoneme.upper() in w["focusSound"]]
        if not warmups:
            # Fallback to jaw drop
            warmups = [VOCAL_WARMUPS[3]]

        drills = cls.get_drills_for_sound(target_phoneme)

        return {
            "targetPhoneme": target_phoneme,
            "prescribedWarmups": warmups,
            "neuromuscularDrills": drills,
            "coachingTip": f"Perform this sequence of warm-ups for 2 minutes before reciting tongue twisters starting with the /{target_phoneme}/ sound."
        }
