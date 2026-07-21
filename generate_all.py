#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
import time

DB_FILE = os.path.join(os.path.dirname(__file__), "data", "db.json")

LANGUAGES = [
    "English",
    "Spanish",
    "French",
    "German",
    "Hindi",
    "Tamil",
    "Telugu",
    "Kannada"
]

CATEGORIES = ["Animals", "Food", "SciFi", "General"]
DIFFICULTIES = ["easy", "medium", "hard"]

def load_db():
    if not os.path.exists(DB_FILE):
        return {"tongueTwisters": [], "practiceAttempts": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading DB: {e}")
        return {"tongueTwisters": [], "practiceAttempts": []}

def save_db(db):
    try:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        print(f"Saved DB to {DB_FILE}")
    except Exception as e:
        print(f"Error saving DB: {e}")

def generate_tongue_twister(api_key, language, difficulty, theme):
    print(f"Generating tongue twister for {language} ({difficulty}, {theme})...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    
    prompt = f"""Generate a single extremely tricky, fun, and phonetic-challenging tongue twister with the following properties:
- Language: {language}
- Difficulty Level: {difficulty} (where 'easy' has simple words, 'medium' is normal, 'hard' has extremely difficult alternating phonemes/letters)
- Theme/Category: {theme}

Ensure that it is actual, grammatically correct, and authentic tongue twister phrasing in the requested language (using native script where applicable, like Devanagari for Hindi, Tamil script for Tamil, Telugu script for Telugu, Kannada script for Kannada). Provide a short description in English explaining what it means.

Format your response as a valid JSON object matching this exact schema:
{{
  "text": "The actual tongue twister in native script (with transliteration in parentheses if non-Latin)",
  "focusSound": "The letter or phoneme pair that is emphasized, e.g. 'Sh' or 'ழ (zha)' or 'క (ka)'",
  "category": "The theme category, e.g. 'Animals', 'Food', 'SciFi'",
  "meaning": "A brief, humorous 1-sentence translation/explanation in English of what the tongue twister means."
}}"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "text": {"type": "STRING"},
                    "focusSound": {"type": "STRING"},
                    "category": {"type": "STRING"},
                    "meaning": {"type": "STRING"}
                },
                "required": ["text", "focusSound", "category", "meaning"]
            }
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text_out = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text_out.strip())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"General Error during API call: {e}")
        return None

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "MY_GEMINI_API_KEY":
        print("Error: GEMINI_API_KEY environment variable is missing or is placeholder.")
        print("Please configure your GEMINI_API_KEY in Settings or run with GEMINI_API_KEY=your_key python3 generate_all.py")
        sys.exit(1)

    db = load_db()
    existing_twisters = db.get("tongueTwisters", [])

    print(f"Loaded {len(existing_twisters)} existing tongue twisters from database.")
    print("Beginning generation for all 8 supported languages...")

    generated_count = 0

    # We will generate 1 new custom tongue twister per language to expand our library beautifully!
    # Stagger categories and difficulties to have a rich mix.
    for i, lang in enumerate(LANGUAGES):
        difficulty = DIFFICULTIES[i % len(DIFFICULTIES)]
        theme = CATEGORIES[(i + 1) % len(CATEGORIES)]
        
        # Check if we already have many twisters for this language. If we want to enrich them, we add a new one.
        result = generate_tongue_twister(api_key, lang, difficulty, theme)
        if result:
            new_id = f"gen-py-{int(time.time())}-{i}"
            new_twister = {
                "id": new_id,
                "text": result.get("text"),
                "language": lang,
                "difficulty": difficulty,
                "category": result.get("category", theme),
                "focusSound": result.get("focusSound", "Generic"),
                "meaning": result.get("meaning", "Generated by Python engine"),
                "likes": 0,
                "attemptCount": 0,
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            db["tongueTwisters"].append(new_twister)
            generated_count += 1
            print(f"Successfully generated and added: {new_twister['text'][:50]}... ({lang})")
            save_db(db) # Save incrementally
            time.sleep(1) # Prevent rate limiting

    print(f"\nCompleted! Generated {generated_count} new tongue twisters using Python + Gemini API.")

if __name__ == "__main__":
    main()
