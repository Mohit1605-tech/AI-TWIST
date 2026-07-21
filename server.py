# -*- coding: utf-8 -*-
"""
Main Python Flask Web Server for Tongue Twister Vocal Arena.
Serves static React frontend files from 'dist/' and hosts a suite of full-stack API endpoints.
Powered by customized local Python modules: DatabaseManager, PronunciationEngine, AICoach,
PhoneticDictionary, and VocalAnalyticsReport.
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory

# Import local Python business-logic and database modules
from database_manager import DatabaseManager
from pronunciation_engine import PronunciationEngine
from ai_coach import AICoach
from phonetic_dictionary import PhoneticDictionary
from vocal_analytics_report import VocalAnalyticsReport

app = Flask(__name__, static_folder="dist", static_url_path="")
PORT = 3000

# Initialize Database Manager
DB_FILE_PATH = os.path.join(os.getcwd(), "data", "db.json")
db_manager = DatabaseManager(DB_FILE_PATH)

# Initialize AI Coach
ai_coach = AICoach()

def create_fallback_twister(language, difficulty, theme, focus_sound):
    language_fallbacks = {
        "Tamil": {
            "text": "யாழ்ப்பாயாத்து பலாப்பழம் வழுக்கி விழுந்தது.",
            "meaning": "The Jaffna jackfruit slipped and fell (emphasizes the retroflex 'zha' sound unique to Tamil).",
            "transliteration": "Yaazhpaanathu palaapazham vazhukki vizhundhadhu.",
            "focus": "ழ (zha)"
        },
        "Telugu": {
            "text": "కాకి కాక కాకికి కాక కాకపోతే కాకికి కాక మరేమిటి?",
            "meaning": "If a crow doesn't feel hot, who else would feel hot if not a crow? (utilizes phonetic play on ka-ka).",
            "transliteration": "Kaaki kaaka kaakiki kaaka kaakapothe kaakiki kaaka maremiti?",
            "focus": "క (ka)"
        },
        "Kannada": {
            "text": "ಕಾಗೆ ಪುಕ್ಕ ಗುಬ್ಬಿ ಪುಕ್ಕ",
            "meaning": "Crow's feather, sparrow's feather (alternating 'pukka' with birds).",
            "transliteration": "Kaage pukka gubbi pukka",
            "focus": "P (pukka)"
        },
        "Hindi": {
            "text": "सत्तर शेरनी शीशे में शर्मीले सियार को सताती हैं।",
            "meaning": "Seventy lionesses tease a shy jackal in the mirror.",
            "transliteration": "Sattar sherni sheeshe mein sharmile siyaar ko sataati hain.",
            "focus": "Sh / S (श / स)"
        },
        "Spanish": {
            "text": "Tres tristes tigres tragaban trigo en un trigal en tres tristes trastos.",
            "meaning": "Three sad tigers were swallowing wheat in a wheat field in three sad dishes.",
            "transliteration": "Tres tristes tigres tragaban trigo en un trigal en tres tristes trastos.",
            "focus": "Tr"
        },
        "French": {
            "text": "Un chasseur sachant chasser doit savoir chasser sans son chien.",
            "meaning": "A hunter who knows how to hunt must know how to hunt without his dog.",
            "transliteration": "Un chasseur sachant chasser doit savoir chasser sans son chien.",
            "focus": "Ch / S"
        },
        "German": {
            "text": "Fischers Fritz fischt frische Fische, frische Fische fischt Fischers Fritz.",
            "meaning": "Fisherman Fritz is fishing for fresh fish, fresh fish are fished by Fisherman Fritz.",
            "transliteration": "Fischers Fritz fischt frische Fische, frische Fische fischt Fischers Fritz.",
            "focus": "F"
        },
        "English": {
            "text": "Super silly snakes singing songs about S.",
            "meaning": "A generated fallback tongue twister focusing on S.",
            "transliteration": "Super silly snakes singing songs about S.",
            "focus": "S"
        }
    }

    letters = focus_sound.upper() if focus_sound else "S"
    fallback_text = ""
    fallback_transliteration = ""
    fallback_meaning = ""
    focus_desc = letters

    if language in language_fallbacks:
        fallback_text = language_fallbacks[language]["text"]
        fallback_meaning = language_fallbacks[language]["meaning"]
        fallback_transliteration = language_fallbacks[language]["transliteration"]
        focus_desc = language_fallbacks[language]["focus"]
    else:
        fallback_themes = {
            "Animals": ["silly snakes singing songs", "fidgety frogs fishing flying flies", "crazy cats cooking carrots"],
            "Food": ["tasty tacos tumbling town", "sweet strawberry syrup sliding slowly", "greasy garlic grapes glowing green"],
            "SciFi": ["robotic rovers running rusty rings", "alien astronauts altering active atmosphere", "cosmic comets crashing cold craters"]
        }
        themes_list = fallback_themes.get(theme, fallback_themes["Animals"])
        import random
        rand_phrase = random.choice(themes_list)
        fallback_text = f"Super silly {rand_phrase}. Specialized speech testing sound {letters} repetitively."
        fallback_meaning = f"A generated story focusing heavily on the sound of the letter '{letters}' in a {theme} setting."
        fallback_transliteration = fallback_text

    return {
        "id": f"gen-{int(time.time() * 1000)}",
        "text": fallback_text,
        "language": language,
        "difficulty": difficulty,
        "category": theme,
        "focusSound": focus_desc,
        "meaning": fallback_meaning,
        "transliteration": fallback_transliteration,
        "likes": 0,
        "attemptCount": 0,
        "createdAt": datetime.now().isoformat() + "Z"
    }

@app.route("/api/health", methods=["GET"])
def health():
    """Simple service health probe."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_modules": {
            "database_manager": "active",
            "pronunciation_engine": "active",
            "ai_coach": "active" if ai_coach.has_credentials() else "fallback",
            "phonetic_dictionary": "active",
            "vocal_analytics_report": "active"
        }
    })

@app.route("/style.css", methods=["GET"])
def serve_fallback_style():
    return send_from_directory(os.getcwd(), "style.css")

@app.route("/simple.html", methods=["GET"])
def serve_simple_html():
    return send_from_directory(os.getcwd(), "simple.html")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET"])
def serve_index(path):
    static_file = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_file):
        return send_from_directory(app.static_folder, path)

    index_file = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(app.static_folder, "index.html")

    return send_from_directory(os.getcwd(), "simple.html")

@app.route("/api/twisters", methods=["GET"])
def get_twisters():
    """Retrieves all tongue twisters, with optional language and query filtering."""
    language = request.args.get("language")
    difficulty = request.args.get("difficulty")
    query = request.args.get("query")
    
    twisters = db_manager.get_tongue_twisters(
        language=language,
        difficulty=difficulty,
        query=query
    )
    return jsonify(twisters)

@app.route("/api/twisters/<string:twister_id>/like", methods=["POST"])
def like_twister(twister_id):
    """Likes a specific tongue twister."""
    new_likes = db_manager.increment_likes(twister_id)
    if new_likes is not None:
        return jsonify({"success": True, "likes": new_likes})
    return jsonify({"error": f"Tongue twister with ID '{twister_id}' not found."}), 404

@app.route("/api/twisters/<string:twister_id>/attempts", methods=["POST"])
def add_attempt(twister_id):
    """Saves a practice attempt and updates metrics on the parent twister."""
    req_data = request.get_json() or {}
    spoken_text = req_data.get("spokenText", "")
    accuracy = req_data.get("accuracy")
    wpm = req_data.get("wpm")
    duration_ms = req_data.get("durationMs", 0)

    if accuracy is None or wpm is None:
        return jsonify({"error": "Missing accuracy or wpm parameters."}), 400

    attempt_payload = {
        "spokenText": spoken_text,
        "accuracy": accuracy,
        "wpm": wpm,
        "durationMs": duration_ms
    }

    success, attempt, twister = db_manager.add_practice_attempt(twister_id, attempt_payload)
    if success:
        return jsonify({
            "success": True,
            "attempt": attempt,
            "twister": twister
        })
    return jsonify({"error": f"Tongue twister with ID '{twister_id}' not found."}), 404

@app.route("/api/analyze_speech", methods=["POST"])
def analyze_speech():
    """
     LINGUISTIC PIPELINE (Runs entirely on the Python backend)
    Analyzes and aligns user's speech transcription against target twister.
    Returns: Word-by-word diff array, accuracy score, and calculated WPM.
    Now enriched with sibilant / acoustic collision profiling from PhoneticDictionary!
    """
    req_data = request.get_json() or {}
    target_text = req_data.get("targetText", "")
    spoken_text = req_data.get("spokenText", "")
    duration_ms = req_data.get("durationMs", 0)

    if not target_text:
        return jsonify({"error": "Target tongue twister text is required for alignment."}), 400

    # Execute sequence alignment in Python
    alignment, accuracy = PronunciationEngine.calculate_alignment(target_text, spoken_text)
    wpm = PronunciationEngine.calculate_wpm(spoken_text, duration_ms)

    # Phonetic collisions analysis from PhoneticDictionary
    collisions = PhoneticDictionary.analyze_phonetic_collisions(target_text)
    collisions_list = [{"sound": name, "intensity": count} for name, count in collisions if count > 0]

    return jsonify({
        "success": True,
        "wordDiff": alignment,
        "accuracy": accuracy,
        "wpm": wpm,
        "durationMs": duration_ms,
        "phoneticCollisions": collisions_list
    })

@app.route("/api/coach", methods=["POST"])
def coach_insights():
    """
     AI PHONETIC INSTRUCTOR (Runs entirely on the Python backend)
    Generates vocal coach guidance based on missed/partial words.
    """
    req_data = request.get_json() or {}
    twister_text = req_data.get("twisterText", "")
    spoken_text = req_data.get("spokenText", "")
    accuracy = req_data.get("accuracy", 0)
    wpm = req_data.get("wpm", 0)
    difficulty = request.get("difficulty", "medium")
    missed_words = req_data.get("missedWords", [])
    partial_words = req_data.get("partialWords", [])

    if not twister_text:
        return jsonify({"error": "Tongue twister text is required."}), 400

    feedback = ai_coach.generate_feedback(
        twister_text=twister_text,
        spoken_text=spoken_text,
        accuracy=accuracy,
        wpm=wpm,
        difficulty=difficulty,
        missed_words=missed_words,
        partial_words=partial_words
    )

    return jsonify({
        "success": True,
        "insights": feedback
    })

@app.route("/api/analytics/report", methods=["GET"])
def get_vocal_report():
    """
     VOCAL ANALYTICS ENGINE (Runs entirely on the Python backend)
    Computes streaks, consistency trends, and returns a markdown progress report.
    """
    db = db_manager.read_all()
    attempts = db.get("practiceAttempts", [])
    twisters = db.get("tongueTwisters", [])
    
    reporter = VocalAnalyticsReport(attempts, twisters)
    markdown_report = reporter.generate_analytical_report()
    
    return jsonify({
        "success": True,
        "report": markdown_report
    })

@app.route("/api/twisters/generate", methods=["POST"])
def generate_twister():
    """Generates tongue twister using Gemini-3.1-flash-lite, with robust local fallback."""
    req_data = request.get_json() or {}
    language = req_data.get("language", "English")
    difficulty = req_data.get("difficulty", "medium")
    theme = req_data.get("theme", "General")
    focus_sound = req_data.get("focusSound")
    length = req_data.get("length", "medium")

    key = os.environ.get("GEMINI_API_KEY")
    if not key or key == "MY_GEMINI_API_KEY":
        # GRACEFUL FALLBACK (Same fallback structure but using robust Python random choice)
        language_fallbacks = {
            "Tamil": {
                "text": "யாழ்ப்பாணத்து பலாப்பழம் வழுக்கி விழுந்தது.",
                "meaning": "The Jaffna jackfruit slipped and fell (emphasizes the retroflex 'zha' sound unique to Tamil).",
                "transliteration": "Yaazhpaanathu palaapazham vazhukki vizhundhadhu.",
                "focus": "ழ (zha)"
            },
            "Telugu": {
                "text": "కాకి కాక కాకికి కాక కాకపోతే కాకికి కాక మరేమిటి?",
                "meaning": "If a crow doesn't feel hot, who else would feel hot if not a crow? (utilizes phonetic play on ka-ka).",
                "transliteration": "Kaaki kaaka kaakiki kaaka kaakapothe kaakiki kaaka maremiti?",
                "focus": "క (ka)"
            },
            "Kannada": {
                "text": "ಕಾಗೆ ಪುಕ್ಕ ಗುಬ್ಬಿ ಪುಕ್ಕ",
                "meaning": "Crow's feather, sparrow's feather (alternating 'pukka' with birds).",
                "transliteration": "Kaage pukka gubbi pukka",
                "focus": "P (pukka)"
            },
            "Hindi": {
                "text": "सत्तर शेरनी शीशे में शर्मीले सियार को सताती हैं।",
                "meaning": "Seventy lionesses tease a shy jackal in the mirror.",
                "transliteration": "Sattar sherni sheeshe mein sharmile siyaar ko sataati hain.",
                "focus": "Sh / S (श / स)"
            },
            "Spanish": {
                "text": "Tres tristes tigres tragaban trigo en un trigal en tres tristes trastos.",
                "meaning": "Three sad tigers were swallowing wheat in a wheat field in three sad dishes.",
                "transliteration": "Tres tristes tigres tragaban trigo en un trigal en tres tristes trastos.",
                "focus": "Tr"
            },
            "French": {
                "text": "Un chasseur sachant chasser doit savoir chasser sans son chien.",
                "meaning": "A hunter who knows how to hunt must know how to hunt without his dog.",
                "transliteration": "Un chasseur sachant chasser doit savoir chasser sans son chien.",
                "focus": "Ch / S"
            },
            "German": {
                "text": "Fischers Fritz fischt frische Fische, frische Fische fischt Fischers Fritz.",
                "meaning": "Fisherman Fritz is fishing for fresh fish, fresh fish are fished by Fisherman Fritz.",
                "transliteration": "Fischers Fritz fischt frische Fische, frische Fische fischt Fischers Fritz.",
                "focus": "F"
            }
        }

        fallback_text = ""
        fallback_meaning = ""
        fallback_transliteration = ""
        letters = focus_sound.upper() if focus_sound else "S"

        if language in language_fallbacks:
            fallback_text = language_fallbacks[language]["text"]
            fallback_meaning = language_fallbacks[language]["meaning"]
            fallback_transliteration = language_fallbacks[language]["transliteration"]
            letters = language_fallbacks[language]["focus"]
        else:
            fallback_themes = {
                "Animals": ["silly snakes singing songs", "fidgety frogs fishing flying flies", "crazy cats cooking carrots"],
                "Food": ["tasty tacos tumbling town", "sweet strawberry syrup sliding slowly", "greasy garlic grapes glowing green"],
                "SciFi": ["robotic rovers running rusty rings", "alien astronauts altering active atmosphere", "cosmic comets crashing cold craters"]
            }
            themes_list = fallback_themes.get(theme, fallback_themes["General"])
            import random
            rand_phrase = random.choice(themes_list)
            fallback_text = f"Super silly {rand_phrase}. Specialized speech testing sound {letters} repetitively."
            fallback_meaning = f"A generated story focusing heavily on the sound of the letter '{letters}' in a {theme} setting."
            fallback_transliteration = fallback_text

        fallback_twister = {
            "id": f"gen-{int(time.time() * 1000)}",
            "text": fallback_text,
            "language": language,
            "difficulty": difficulty,
            "category": theme,
            "focusSound": letters,
            "meaning": fallback_meaning,
            "transliteration": fallback_transliteration,
            "likes": 0,
            "attemptCount": 0,
            "createdAt": datetime.now().isoformat() + "Z"
        }

        db_manager.add_tongue_twister(fallback_twister)
        return jsonify({
            "success": True,
            "twister": fallback_twister,
            "isFallback": True
        })

    focus_sound_desc = f"Heavy focus on the sound of '{focus_sound}'" if focus_sound else "Any fun letter/combination (e.g. s, p, th, sh, etc.)"
    prompt_text = (
        f"Generate a tongue twister with the following properties:\n"
        f"- Language: {language}\n"
        f"- Difficulty Level: {difficulty} (where 'easy' has simple words, 'medium' is normal, 'hard' has extremely difficult alternating phonemes)\n"
        f"- Theme/Category: {theme}\n"
        f"- Focus Sound (Target Phoneme): {focus_sound_desc}\n"
        f"- Length: {length} (short/medium/long)\n\n"
        f"Ensure that it is actual, grammatical text in the requested language that is extremely hard to say fast due to alternating phonetic structures.\n"
        f"If the requested language is not English (e.g. Tamil, Telugu, Kannada, Hindi, Spanish, French, German), you MUST write the 'text' property in the native script (for example, Tamil script for Tamil, Kannada script for Kannada, Hindi script for Hindi, Telugu script for Telugu, etc.) AND provide the phonetic transliteration/pronunciation in English alphabets in the 'transliteration' property. If the requested language is English, 'transliteration' should be equal to 'text'."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={key}"
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt_text
            }]
        }],
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are an expert phonetician, linguist, and creative writer specializing in creating extremely catchy, fun, and phonetic-challenging tongue twisters.\n"
                    "You must always output your response as a valid JSON object matching this exact schema:\n"
                    "{\n"
                    "  \"text\": \"The actual tongue twister itself in native script\",\n"
                    "  \"transliteration\": \"The phonetic pronunciation in English alphabets (or same as text if English)\",\n"
                    "  \"focusSound\": \"The letter or phoneme pair that is emphasized, e.g. 'Sh' or 'P'\",\n"
                    "  \"category\": \"The theme category, e.g. 'Animals', 'Food', 'SciFi'\",\n"
                    "  \"meaning\": \"A brief, humorous 1-sentence translation/explanation of what the tongue twister means.\"\n"
                    "}"
                )
            }]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "text": { "type": "STRING" },
                    "transliteration": { "type": "STRING" },
                    "focusSound": { "type": "STRING" },
                    "category": { "type": "STRING" },
                    "meaning": { "type": "STRING" }
                },
                "required": ["text", "transliteration", "focusSound", "category", "meaning"]
            }
        }
    }

    try:
        import requests
        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "aistudio-build-python"
            },
            timeout=30
        )
        response.raise_for_status()
        res_data = response.json()
            
        candidate = res_data.get("candidates", [{}])[0]
        text_content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
        
        if not text_content:
            raise ValueError("No response content from Gemini API")
 
        generated = json.loads(text_content.strip())
        
        new_twister = {
            "id": f"gen-{int(time.time() * 1000)}",
            "text": generated.get("text", ""),
            "language": language,
            "difficulty": difficulty,
            "category": generated.get("category", theme),
            "focusSound": generated.get("focusSound", focus_sound or "Generic"),
            "meaning": generated.get("meaning", "A playful phonetic arrangement."),
            "transliteration": generated.get("transliteration", generated.get("text", "")),
            "likes": 0,
            "attemptCount": 0,
            "createdAt": datetime.now().isoformat() + "Z"
        }

        db_manager.add_tongue_twister(new_twister)

        return jsonify({
            "success": True,
            "twister": new_twister
        })

    except Exception as e:
        print("Error during tongue twister generation:", e)

        # If requests or Gemini fail on Render, fallback to a safe local twister.
        fallback_twister = create_fallback_twister(language, difficulty, theme, focus_sound)
        db_manager.add_tongue_twister(fallback_twister)

        return jsonify({
            "success": True,
            "twister": fallback_twister,
            "isFallback": True,
            "error": str(e)
        }), 200

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Computes comprehensive application and diagnostic metrics for dashboard visualizations."""
    db = db_manager.read_all()
    twisters = db.get("tongueTwisters", [])
    attempts = db.get("practiceAttempts", [])

    total_generated = len(twisters)
    total_attempts = len(attempts)

    # Use our Python VocalAnalyticsReport to compute descriptive parameters
    reporter = VocalAnalyticsReport(attempts, twisters)
    streak = reporter.compute_streaks()
    descriptive_stats = reporter.get_vocal_stats()

    average_accuracy = (
        round(sum(a.get("accuracy", 0) for a in attempts) / total_attempts)
        if total_attempts > 0
        else 0
    )
    average_wpm = (
        round(sum(a.get("wpm", 0) for a in attempts) / total_attempts)
        if total_attempts > 0
        else 0
    )

    # Difficulty breakdown
    diff_map = {"easy": 0, "medium": 0, "hard": 0}
    for t in twisters:
        diff = t.get("difficulty", "medium").lower()
        diff_map[diff] = diff_map.get(diff, 0) + 1

    difficulty_breakdown = [
        {"name": name.capitalize(), "value": value}
        for name, value in diff_map.items()
    ]

    # Category breakdown
    cat_map = {}
    for t in twisters:
        cat = t.get("category", "General")
        cat_map[cat] = cat_map.get(cat, 0) + 1

    category_breakdown = sorted(
        [{"name": name, "value": value} for name, value in cat_map.items()],
        key=lambda x: x["value"],
        reverse=True
    )[:5]

    # Focus sound breakdown
    sound_map = {}
    for t in twisters:
        s = t.get("focusSound", "Generic").upper()
        sound_map[s] = sound_map.get(s, 0) + 1

    sound_breakdown = sorted(
        [{"name": name, "value": value} for name, value in sound_map.items()],
        key=lambda x: x["value"],
        reverse=True
    )[:5]

    # Progress over time (chronological grouping)
    date_map = {}
    for a in attempts:
        timestamp_str = a.get("timestamp")
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            date_str = dt.strftime("%b %d")
        except Exception:
            date_str = "Recent"

        if date_str not in date_map:
            date_map[date_str] = {"totalAcc": 0, "totalWpm": 0, "count": 0}
        
        date_map[date_str]["totalAcc"] += a.get("accuracy", 0)
        date_map[date_str]["totalWpm"] += a.get("wpm", 0)
        date_map[date_str]["count"] += 1

    progress_data = [
        {
            "date": date_str,
            "accuracy": round(data["totalAcc"] / data["count"]),
            "wpm": round(data["totalWpm"] / data["count"])
        }
        for date_str, data in date_map.items()
    ]
    
    sorted_progress = progress_data[-10:]

    return jsonify({
        "totalGenerated": total_generated,
        "totalAttempts": total_attempts,
        "averageAccuracy": average_accuracy,
        "averageWpm": average_wpm,
        "difficultyBreakdown": difficulty_breakdown,
        "categoryBreakdown": category_breakdown,
        "soundBreakdown": sound_breakdown,
        "progressData": sorted_progress,
        "practiceStreak": streak,
        "varianceAccuracy": descriptive_stats["varianceAccuracy"]
    })

@app.route("/api/python/run", methods=["POST"])
def run_python_script():
    """Runs seed-generator script."""
    script_path = os.path.join(os.getcwd(), "generate_all.py")
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=45
        )
        success = (result.returncode == 0)
        return jsonify({
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": None if success else f"Exit code {result.returncode}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "error": str(e)
        }), 500

@app.route("/api/python/code", methods=["GET"])
def get_python_code():
    """Reads script content."""
    script_path = os.path.join(os.getcwd(), "generate_all.py")
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()
        return jsonify({"code": code})
    except Exception as e:
        return jsonify({"error": "Failed to read python script file"}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Fallback router serving built SPA index.html for unknown client routes."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    print(f"Starting modularized Python Flask web server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT)
