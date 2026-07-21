# -*- coding: utf-8 -*-
"""
AI Coach Module for Tongue Twister Vocal Arena.
Uses the Gemini API (specifically gemini-3.1-flash-lite) to deliver custom phonetic feedback,
identifying the exact consonant or vowel collisions causing difficulty, and generating
specialized articulation drills to help users improve their scores.
"""

import os
import json
from typing import Dict, List, Any, Optional

class AICoach:
    """
    Phonetic AI Coach using Gemini API to generate personalized vocal feedback
    based on the user's missed and partially-pronounced words.
    """

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

    def has_credentials(self) -> bool:
        """Checks if a valid Gemini API key is available in the environment."""
        return bool(self.api_key and self.api_key != "MY_GEMINI_API_KEY")

    def generate_feedback(self, 
                          twister_text: str, 
                          spoken_text: str, 
                          accuracy: int, 
                          wpm: int, 
                          difficulty: str,
                          missed_words: List[str], 
                          partial_words: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Requests structured coaching suggestions from Gemini based on the attempt results.
        If the API key is not present or an error occurs, returns a structured fallback.
        """
        if not self.has_credentials():
            return self._get_fallback_feedback(twister_text, accuracy, missed_words, partial_words)

        # Structure missed and partial words for prompt context
        missed_str = ", ".join(missed_words) if missed_words else "None"
        partials_list = [f"'{p['target']}' (pronounced like '{p['spoken']}')" for p in partial_words]
        partials_str = ", ".join(partials_list) if partials_list else "None"

        prompt = (
            f"As a friendly, professional speech-language pathologist and accent coach, analyze this tongue twister practice attempt:\n"
            f"- Tongue Twister: \"{twister_text}\"\n"
            f"- User's Transcription: \"{spoken_text}\"\n"
            f"- Articulation Accuracy: {accuracy}%\n"
            f"- Speech Rate: {wpm} Words Per Minute (WPM)\n"
            f"- Difficulty Level: {difficulty}\n"
            f"- Entirely Skipped/Missed Words: {missed_str}\n"
            f"- Partially Mispronounced Words: {partials_str}\n\n"
            f"Provide an actionable, friendly speech coaching review with:\n"
            f"1. A structural diagnosis of which phonetic sounds (e.g. sibilants, dental plosives) caused the collision.\n"
            f"2. Three target articulation tips (e.g. jaw alignment, tongue position, slowing speed).\n"
            f"3. A personalized, short, fun 1-line vocal warm-up drill to practice the problematic sounds."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "systemInstruction": {
                "parts": [{
                    "text": (
                        "You are an encouraging and incredibly knowledgeable AI Vocal Coach specializing in phonetics, articulation, and voice acting.\n"
                        "You must always reply in structured JSON matching this exact schema:\n"
                        "{\n"
                        "  \"diagnosis\": \"Brief, warm 2-3 sentence explanation of the specific phonetic sounds that proved difficult during this attempt.\",\n"
                        "  \"tips\": [\n"
                        "    \"Tip 1: Concrete physical instruction for mouth/tongue/breath adjustment.\",\n"
                        "    \"Tip 2: Concrete physical instruction.\",\n"
                        "    \"Tip 3: Concrete physical instruction.\"\n"
                        "  ],\n"
                        "  \"warmUpDrill\": \"A short, fun, 1-line phonetic drill focusing specifically on the difficult sounds.\"\n"
                        "}"
                    )
                }]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "diagnosis": { "type": "STRING" },
                        "tips": {
                            "type": "ARRAY",
                            "items": { "type": "STRING" }
                        },
                        "warmUpDrill": { "type": "STRING" }
                    },
                    "required": ["diagnosis", "tips", "warmUpDrill"]
                }
            }
        }

        try:
            import requests
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json", "User-Agent": "aistudio-vocal-arena-coach"},
                timeout=15
            )
            response.raise_for_status()
            res_data = response.json()
            
            candidate = res_data.get("candidates", [{}])[0]
            text_content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if text_content:
                return json.loads(text_content.strip())
        except Exception as e:
            print("Error retrieving AI coaching feedback:", e)

        # Fallback if request fails
        return self._get_fallback_feedback(twister_text, accuracy, missed_words, partial_words)

    def _get_fallback_feedback(self, twister_text: str, accuracy: int, missed_words: List[str], partial_words: List[Dict[str, str]]) -> Dict[str, Any]:
        """Provides high-quality, pre-computed structured phonetic tips if Gemini is unavailable."""
        
        # Determine likely focus sounds
        words_of_interest = missed_words + [p["target"] for p in partial_words]
        sounds = []
        for w in words_of_interest:
            if w.lower().startswith(("sh", "ch", "th", "ph")):
                sounds.append(w[:2].lower())
            elif w:
                sounds.append(w[0].lower())
        
        sounds_unique = list(set(sounds))[:2]
        sounds_str = " and ".join([f"'{s.upper()}'" for s in sounds_unique]) if sounds_unique else "consonant shifts"

        diagnosis = f"Fantastic effort! Your performance shows great vocal control, but alternating {sounds_str} sounds can sometimes tie tongue knots."
        
        if accuracy >= 90:
            tips = [
                "Incredible articulation! Focus on speeding up slightly to challenge your muscle memory.",
                "To gain absolute mastery, try projecting from your diaphragm to keep words crisp and sharp.",
                "Keep your jaw relaxed and let your lips do the heavy lifting for micro-movements."
            ]
            warm_up = "Sally silently swept seven silver seashells."
        else:
            tips = [
                "Slightly slow down your tempo (aim for about 70-80 WPM) until your muscle memory locks in.",
                "Over-articulate the starting consonants of each word, taking a brief breath before difficult transitions.",
                "Ensure your tongue tip taps the alveolar ridge sharply when shifting between letters."
            ]
            warm_up = f"Tip of the tongue, the teeth, the lips, practicing the {sounds_str or 'vowels'}."

        return {
            "diagnosis": diagnosis,
            "tips": tips,
            "warmUpDrill": warm_up
        }
