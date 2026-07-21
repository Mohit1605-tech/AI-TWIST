const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;
app.use(express.json());

const DB_PATH = path.join(process.cwd(), 'data', 'db.json');

function readDb() {
  try {
    const raw = fs.readFileSync(DB_PATH, 'utf-8');
    return JSON.parse(raw);
  } catch (e) {
    return { tongueTwisters: [], practiceAttempts: [] };
  }
}

function writeDb(db) {
  try {
    fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), 'utf-8');
  } catch (e) {
    console.error('Failed to write DB:', e);
  }
}

// Serve static frontend build
app.use(express.static(path.join(process.cwd(), 'dist')));

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', now: new Date().toISOString() });
});

app.get('/api/twisters', (req, res) => {
  const db = readDb();
  res.json(db.tongueTwisters || []);
});

app.post('/api/twisters/generate', (req, res) => {
  const { language = 'English', difficulty = 'medium', theme = 'General', focusSound } = req.body || {};

  const letters = (focusSound || 'S').toString();
  const language_fallbacks = {
    Tamil: {
      text: 'யாழ்ப்பாணத்து பலாப்பழம் வழுக்கி விழுந்தது.',
      transliteration: 'Yaazhpaanathu palaapazham vazhukki vizhundhadhu.',
      meaning: "The Jaffna jackfruit slipped and fell (emphasizes the retroflex 'zha' sound unique to Tamil).",
      focus: 'ழ (zha)'
    },
    Telugu: {
      text: 'కాకి కాక కాకికి కాక కాకపోతే కాకికి కాక మరేమిటి?',
      transliteration: 'Kaaki kaaka kaakiki kaaka kaakapothe kaakiki kaaka maremiti?',
      meaning: "If a crow doesn't feel hot, who else would feel hot if not a crow? (utilizes phonetic play on ka-ka).",
      focus: 'క (ka)'
    },
    Kannada: {
      text: 'ಕಾಗೆ ಪುಕ್ಕ ಗುಬ್ಬಿ ಪುಕ್ಕ',
      transliteration: 'Kaage pukka gubbi pukka',
      meaning: "Crow's feather, sparrow's feather (alternating 'pukka' with birds).",
      focus: 'P (pukka)'
    },
    Hindi: {
      text: 'सत्तर शेरनी शीशे में शर्मीले सियार को सताती हैं।',
      transliteration: 'Sattar sherni sheeshe mein sharmile siyaar ko sataati hain.',
      meaning: "Seventy lionesses tease a shy jackal in the mirror.",
      focus: 'Sh / S (श / स)'
    },
    Spanish: {
      text: 'Tres tristes tigres tragaban trigo en un trigal en tres tristes trastos.',
      transliteration: 'Tres tristes tigres tragaban trigo en un trigal en tres tristes trastos.',
      meaning: 'Three sad tigers were swallowing wheat in a wheat field in three sad dishes.',
      focus: 'Tr'
    },
    French: {
      text: 'Un chasseur sachant chasser doit savoir chasser sans son chien.',
      transliteration: 'Un chasseur sachant chasser doit savoir chasser sans son chien.',
      meaning: 'A hunter who knows how to hunt must know how to hunt without his dog.',
      focus: 'Ch / S'
    },
    German: {
      text: 'Fischers Fritz fischt frische Fische, frische Fische fischt Fischers Fritz.',
      transliteration: 'Fischers Fritz fischt frische Fische, frische Fische fischt Fischers Fritz.',
      meaning: 'Fisherman Fritz is fishing for fresh fish, fresh fish are fished by Fisherman Fritz.',
      focus: 'F'
    },
    English: {
      text: `Super silly snakes singing songs about ${letters}.`,
      transliteration: `Super silly snakes singing songs about ${letters}.`,
      meaning: `A generated fallback tongue twister focusing on ${letters}.`,
      focus: letters
    }
  };

  let fallback_text = `Super silly ${theme.toLowerCase()} phrase focusing on ${letters}.`;
  let fallback_translit = fallback_text;
  let fallback_meaning = `A generated fallback tongue twister focusing on ${letters}.`;
  let focus_desc = letters;

  if (language_fallbacks[language]) {
    fallback_text = language_fallbacks[language].text;
    fallback_translit = language_fallbacks[language].transliteration || language_fallbacks[language].text;
    fallback_meaning = language_fallbacks[language].meaning || fallback_meaning;
    focus_desc = language_fallbacks[language].focus || focus_desc;
  }

  const twister = {
    id: `gen-${Date.now()}`,
    text: fallback_text,
    language,
    difficulty,
    category: theme,
    focusSound: focus_desc,
    meaning: fallback_meaning,
    transliteration: fallback_translit,
    likes: 0,
    attemptCount: 0,
    createdAt: new Date().toISOString()
  };

  const db = readDb();
  db.tongueTwisters = db.tongueTwisters || [];
  db.tongueTwisters.unshift(twister);
  writeDb(db);

  res.json({ success: true, twister, isFallback: true });
});

// Fallback route to serve index.html for SPA routes
app.get('*', (req, res) => {
  const indexPath = path.join(process.cwd(), 'dist', 'index.html');
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).send('Not found');
  }
});

app.listen(PORT, () => {
  console.log(`Dev server with fallback API running on http://localhost:${PORT}`);
});
