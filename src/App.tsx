/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Sparkles, Mic, BookOpen, Activity, AlertCircle, RefreshCw, 
  Smile, Flame, Award, HelpCircle, Volume2, Heart, Copy, Check, Info, Share2, Square, Save, RotateCcw, Search, Filter, Zap
} from 'lucide-react';
import { motion } from 'motion/react';
import { 
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  BarChart, Bar, PieChart, Pie, Cell 
} from 'recharts';
import confetti from 'canvas-confetti';

export interface TongueTwister {
  id: string;
  text: string;
  language: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  focusSound: string;
  meaning?: string;
  transliteration?: string;
  likes: number;
  attemptCount: number;
  averageAccuracy?: number;
}

export interface PracticeAttempt {
  id: string;
  twisterId: string;
  spokenText: string;
  accuracy: number;
  wpm: number;
  durationMs: number;
  timestamp: string;
}

export interface DashboardStats {
  totalGenerated: number;
  totalAttempts: number;
  averageAccuracy: number;
  averageWpm: number;
  difficultyBreakdown: { name: string; value: number }[];
  categoryBreakdown: { name: string; value: number }[];
  soundBreakdown: { name: string; value: number }[];
  progressData: { date: string; accuracy: number; wpm: number }[];
  practiceStreak: number;
  varianceAccuracy: number;
}

// Resilient fetch utility
async function fetchWithRetry(url: string, options?: RequestInit, retries = 3, delay = 1000): Promise<Response> {
  try {
    const response = await fetch(url, options);
    if (!response.ok && [500, 502, 503, 504].includes(response.status)) {
      if (retries > 0) {
        await new Promise(res => setTimeout(res, delay));
        return fetchWithRetry(url, options, retries - 1, delay * 1.5);
      }
    }
    return response;
  } catch (err) {
    if (retries > 0) {
      await new Promise(res => setTimeout(res, delay));
      return fetchWithRetry(url, options, retries - 1, delay * 1.5);
    }
    throw err;
  }
}

const COLORS = ['#4f46e5', '#8b5cf6', '#a78bfa', '#c084fc', '#e879f9'];
const DIFFICULTY_COLORS = { 'Easy': '#10b981', 'Medium': '#f59e0b', 'Hard': '#ef4444' };

export default function App() {
  const [activeTab, setActiveTab] = useState<'generate' | 'practice' | 'directory' | 'dashboard'>('generate');
  const [twisters, setTwisters] = useState<TongueTwister[]>([]);
  const [selectedTwister, setSelectedTwister] = useState<TongueTwister | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  
  // App-level Loadings
  const [isLoadingTwisters, setIsLoadingTwisters] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Generator Form State
  const [genLang, setGenLang] = useState('English');
  const [genDiff, setGenDiff] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [genTheme, setGenTheme] = useState('Animals');
  const [genSound, setGenSound] = useState('');

  // Practice Mode State
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [seconds, setSeconds] = useState(0);
  const [durationMs, setDurationMs] = useState(0);
  const [accuracy, setAccuracy] = useState<number | null>(null);
  const [wpm, setWpm] = useState<number | null>(null);
  const [wordDiff, setWordDiff] = useState<{ targetWord: string; spokenWord: string | null; status: 'correct' | 'partial' | 'missed' | 'extra' }[]>([]);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [manualMode, setManualMode] = useState(false);
  const [manualInput, setManualInput] = useState('');
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [coachInsights, setCoachInsights] = useState<{ diagnosis: string; tips: string[]; warmUpDrill: string } | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  // TTS / Voice Guide State
  const [ttsSpeed, setTtsSpeed] = useState<number>(0.75);
  const [ttsVoiceType, setTtsVoiceType] = useState<'bold_indian' | 'native'>('bold_indian');
  const [ttsSourceType, setTtsSourceType] = useState<'transliteration' | 'text'>('transliteration');

  // Directory Search/Filter State
  const [search, setSearch] = useState('');
  const [langFilter, setLangFilter] = useState('All');
  const [diffFilter, setDiffFilter] = useState('All');
  const [themeFilter, setThemeFilter] = useState('All');

  // Dashboard Report State
  const [reportText, setReportText] = useState<string>('');
  const [isReportLoading, setIsReportLoading] = useState<boolean>(false);

  const recognitionRef = useRef<any>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  // Startup Hooks
  useEffect(() => {
    fetchTwisters();
    fetchStats();
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Sync Diagnostics Report when Stats updates
  useEffect(() => {
    if (stats) {
      setIsReportLoading(true);
      fetch('/api/analytics/report')
        .then(res => res.json())
        .then(data => {
          if (data.success) setReportText(data.report);
        })
        .catch(err => console.error('Failed to load analytical report', err))
        .finally(() => setIsReportLoading(false));
    }
  }, [stats]);

  // Reset Practice Arena when Target Twister alters
  useEffect(() => {
    if (selectedTwister) {
      setTranscription('');
      setInterimTranscript('');
      setAccuracy(null);
      setWpm(null);
      setWordDiff([]);
      setSeconds(0);
      setSaveStatus('idle');
      setManualInput('');
      setSpeechError(null);
      setCoachInsights(null);
    }
  }, [selectedTwister]);

  // REST API Operations
  const fetchTwisters = async () => {
    setIsLoadingTwisters(true);
    setErrorMessage(null);
    try {
      const response = await fetchWithRetry('/api/twisters');
      if (!response.ok) throw new Error('Failed to load tongue twisters');
      const data = await response.json();
      setTwisters(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error pulling twister list.');
    } finally {
      setIsLoadingTwisters(false);
    }
  };

  const fetchStats = async () => {
    setIsLoadingStats(true);
    try {
      const response = await fetchWithRetry('/api/stats');
      if (!response.ok) throw new Error('Failed to compute metrics');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleLike = async (id: string) => {
    try {
      const response = await fetchWithRetry(`/api/twisters/${id}/like`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to like twister');
      const result = await response.json();
      setTwisters(prev => prev.map(t => t.id === id ? { ...t, likes: result.likes } : t));
      if (selectedTwister?.id === id) {
        setSelectedTwister(prev => prev ? { ...prev, likes: result.likes } : null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setErrorMessage(null);
    try {
      const response = await fetchWithRetry('/api/twisters/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          language: genLang,
          difficulty: genDiff,
          theme: genTheme,
          focusSound: genSound,
          length: 'medium'
        })
      });
      
      if (!response.ok) throw new Error('Gemini API failed to generate a twister. Try again.');
      const result = await response.json();
      await fetchTwisters();
      setSelectedTwister(result.twister);
      setActiveTab('practice');
    } catch (err: any) {
      setErrorMessage(err.message || 'Unexpected failure generating twister.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Recording Actions
  const startSpeechRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setManualMode(true);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      const langMap: Record<string, string> = {
        English: 'en-US', Spanish: 'es-ES', French: 'fr-FR', German: 'de-DE',
        Hindi: 'hi-IN', Tamil: 'ta-IN', Telugu: 'te-IN', Kannada: 'kn-IN'
      };
      recognition.lang = langMap[selectedTwister?.language || 'English'] || 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        setTranscription('');
        setInterimTranscript('');
        setSeconds(0);
        setAccuracy(null);
        setWpm(null);
        setWordDiff([]);
        setSaveStatus('idle');
        setSpeechError(null);
        setCoachInsights(null);
        
        startTimeRef.current = Date.now();
        timerRef.current = setInterval(() => setSeconds(prev => prev + 1), 1000);
      };

      recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) final += event.results[i][0].transcript;
          else interim += event.results[i][0].transcript;
        }
        if (final) setTranscription(prev => (prev + ' ' + final).trim());
        setInterimTranscript(interim);
      };

      recognition.onerror = (e: any) => {
        setSpeechError(e.error);
        if (e.error === 'not-allowed') setManualMode(true);
        stopRecording();
      };

      recognition.onend = () => {
        setIsRecording(false);
        if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e) {
      setManualMode(true);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) recognitionRef.current.stop();
    setIsRecording(false);
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }

    const finalSpoken = (transcription || interimTranscript).trim();
    if (finalSpoken) processSpeechMetrics(finalSpoken);
  };

  const processSpeechMetrics = async (spokenTextToEvaluate: string) => {
    if (!selectedTwister || !spokenTextToEvaluate.trim()) return;

    setIsAnalyzing(true);
    setSpeechError(null);
    const endTime = Date.now();
    const calculatedDuration = Math.max(1000, endTime - startTimeRef.current);
    setDurationMs(calculatedDuration);

    try {
      const response = await fetchWithRetry('/api/analyze_speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          targetText: selectedTwister.text,
          spokenText: spokenTextToEvaluate,
          durationMs: calculatedDuration
        })
      });

      if (!response.ok) throw new Error("Backend sequence aligner error");
      const result = await response.json();

      setAccuracy(result.accuracy);
      setWpm(result.wpm);
      setWordDiff(result.wordDiff);

      if (result.accuracy >= 90) {
        confetti({ particleCount: 140, spread: 85, origin: { y: 0.6 } });
      }

      const missed = result.wordDiff.filter((w: any) => w.status === 'missed').map((w: any) => w.targetWord);
      const partials = result.wordDiff.filter((w: any) => w.status === 'partial').map((w: any) => ({ target: w.targetWord, spoken: w.spokenWord || '' }));

      const coachResponse = await fetchWithRetry('/api/coach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          twisterText: selectedTwister.text,
          spokenText: spokenTextToEvaluate,
          accuracy: result.accuracy,
          wpm: result.wpm,
          difficulty: selectedTwister.difficulty,
          missedWords: missed,
          partialWords: partials
        })
      });

      if (coachResponse.ok) {
        const coachResult = await coachResponse.json();
        setCoachInsights(coachResult.insights);
      }
    } catch (err: any) {
      setSpeechError("A server communication error occurred during phonetic analysis.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTwister || !manualInput.trim()) return;
    startTimeRef.current = Date.now() - 5000;
    setTranscription(manualInput);
    processSpeechMetrics(manualInput);
  };

  const handleSaveAttempt = async () => {
    if (!selectedTwister || accuracy === null || wpm === null) return;
    setSaveStatus('saving');
    try {
      const response = await fetchWithRetry(`/api/twisters/${selectedTwister.id}/attempts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          spokenText: transcription || manualInput,
          accuracy,
          wpm,
          durationMs
        })
      });
      if (!response.ok) throw new Error('Failed to save practice attempt');
      setSaveStatus('saved');
      fetchTwisters();
      fetchStats();
    } catch (err) {
      setSaveStatus('error');
    }
  };

  const handleReadAloud = (twister: TongueTwister) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      
      // Determine what text content to speak
      let speakText = twister.text;
      if (ttsSourceType === 'transliteration' && twister.transliteration) {
        speakText = twister.transliteration;
      }

      const utterance = new SpeechSynthesisUtterance(speakText);
      utterance.rate = ttsSpeed;

      const voices = window.speechSynthesis.getVoices();
      
      if (ttsVoiceType === 'bold_indian') {
        // Find an Indian English or general Indian voice with bold accent (e.g., en-IN, hi-IN, ta-IN, te-IN, kn-IN)
        // Let's filter for en-IN voices (Indian English)
        let indianVoice = voices.find(v => v.lang.toLowerCase() === 'en-in' && v.name.toLowerCase().includes('male'));
        if (!indianVoice) indianVoice = voices.find(v => v.lang.toLowerCase() === 'en-in' && (v.name.toLowerCase().includes('rishi') || v.name.toLowerCase().includes('hemant') || v.name.toLowerCase().includes('karan') || v.name.toLowerCase().includes('ravi') || v.name.toLowerCase().includes('mohan')));
        if (!indianVoice) indianVoice = voices.find(v => v.lang.toLowerCase() === 'en-in');
        if (!indianVoice) indianVoice = voices.find(v => v.lang.toLowerCase().includes('in'));
        
        if (indianVoice) {
          utterance.voice = indianVoice;
          utterance.lang = indianVoice.lang;
        } else {
          // Fallback to standard en-US or any English voice
          let enVoice = voices.find(v => v.lang.toLowerCase() === 'en-us' && v.name.toLowerCase().includes('male'));
          if (!enVoice) enVoice = voices.find(v => v.lang.toLowerCase().startsWith('en'));
          if (enVoice) {
            utterance.voice = enVoice;
            utterance.lang = enVoice.lang;
          }
        }
        
        // Lower pitch slightly to make the voice "bolder" and more masculine/bold
        utterance.pitch = 0.85; 
      } else {
        // Native speaker mode
        const langMap: Record<string, string> = {
          English: 'en-US', Spanish: 'es-ES', French: 'fr-FR', German: 'de-DE',
          Hindi: 'hi-IN', Tamil: 'ta-IN', Telugu: 'te-IN', Kannada: 'kn-IN'
        };
        const targetLang = langMap[twister.language] || 'en-US';
        utterance.lang = targetLang;
        
        const langPrefix = targetLang.split('-')[0].toLowerCase();
        let nativeVoice = voices.find(v => v.lang.toLowerCase() === targetLang.toLowerCase());
        if (!nativeVoice) nativeVoice = voices.find(v => v.lang.toLowerCase().startsWith(langPrefix));
        
        if (nativeVoice) {
          utterance.voice = nativeVoice;
        }
        
        // For general native voices, make it slightly lower pitch to match "bold male" vibe as well!
        utterance.pitch = 0.92;
      }

      window.speechSynthesis.speak(utterance);
    }
  };

  // Directories Filters
  const uniqueLangs = useMemo(() => ['All', ...Array.from(new Set(twisters.map(t => t.language)))], [twisters]);
  const uniqueThemes = useMemo(() => ['All', ...Array.from(new Set(twisters.map(t => t.category)))], [twisters]);
  const filteredTwisters = useMemo(() => {
    return twisters.filter((t) => {
      const matchSearch = t.text.toLowerCase().includes(search.toLowerCase()) || 
                          (t.meaning || '').toLowerCase().includes(search.toLowerCase()) ||
                          (t.transliteration || '').toLowerCase().includes(search.toLowerCase());
      const matchLang = langFilter === 'All' || t.language === langFilter;
      const matchDiff = diffFilter === 'All' || t.difficulty === diffFilter.toLowerCase();
      const matchTheme = themeFilter === 'All' || t.category === themeFilter;
      return matchSearch && matchLang && matchDiff && matchTheme;
    });
  }, [twisters, search, langFilter, diffFilter, themeFilter]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-between">
      {/* Header Panel */}
      <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6 md:px-8 shrink-0 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-indigo-600 flex items-center justify-center rounded-sm font-bold text-white text-sm">T</div>
          <span className="text-lg md:text-xl font-bold tracking-tight text-slate-800">TWIST.AI</span>
        </div>
        <nav className="flex gap-4 md:gap-8 text-xs font-bold text-slate-500 h-full items-center">
          {[
            { id: 'generate', label: 'Generator' },
            { id: 'practice', label: 'Vocal Arena' },
            { id: 'directory', label: 'Library' },
            { id: 'dashboard', label: 'Diagnostics' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              id={`tab-btn-${tab.id}`}
              className={`py-5 text-[11px] font-bold uppercase tracking-widest border-b-2 h-full transition-all ${
                activeTab === tab.id ? 'text-indigo-600 border-indigo-600' : 'text-slate-400 border-transparent hover:text-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="hidden md:block w-32 text-right">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active</span>
        </div>
      </header>

      {/* Main Body */}
      <main className="max-w-6xl mx-auto w-full px-4 py-8 flex-1">
        {errorMessage && (
          <div className="bg-rose-50 border border-rose-100 text-rose-800 rounded-sm p-4 mb-6 flex gap-3 items-start shadow-sm">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">System Notification</h4>
              <p className="text-xs mt-0.5">{errorMessage}</p>
            </div>
          </div>
        )}

        <div className="space-y-6">
          {/* Tab 1: Generator */}
          {activeTab === 'generate' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-7">
                <form onSubmit={handleGenerate} className="bg-white border border-slate-200 rounded-md p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                    <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-sm"><Sparkles className="w-5 h-5" /></div>
                    <div>
                      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">Concoct Tongue Twister</h3>
                      <p className="text-xs text-slate-400">Powered by server-side Gemini Flash Llama pipeline</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Target Language</label>
                      <select value={genLang} onChange={(e) => setGenLang(e.target.value)} className="w-full bg-slate-50 border border-slate-200 p-2.5 text-xs font-semibold rounded-sm outline-none focus:ring-1 focus:ring-indigo-500">
                        {['English', 'Spanish', 'French', 'German', 'Hindi', 'Tamil', 'Telugu', 'Kannada'].map(l => <option key={l} value={l}>{l}</option>)}
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Vocal Difficulty</label>
                      <select value={genDiff} onChange={(e) => setGenDiff(e.target.value as any)} className="w-full bg-slate-50 border border-slate-200 p-2.5 text-xs font-semibold rounded-sm outline-none focus:ring-1 focus:ring-indigo-500">
                        <option value="easy">Easy Peasy</option>
                        <option value="medium">Mind Bender</option>
                        <option value="hard">Jaw Breaker</option>
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Conceptual Theme</label>
                      <select value={genTheme} onChange={(e) => setGenTheme(e.target.value)} className="w-full bg-slate-50 border border-slate-200 p-2.5 text-xs font-semibold rounded-sm outline-none focus:ring-1 focus:ring-indigo-500">
                        {['Animals', 'Food', 'SciFi', 'General', 'Technology', 'Nature', 'Space'].map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Target Sound Accent</label>
                      <input type="text" value={genSound} onChange={(e) => setGenSound(e.target.value)} placeholder="e.g. S, Sh, P, Tr" className="w-full bg-slate-50 border border-slate-200 p-2 text-xs font-semibold rounded-sm outline-none focus:ring-1 focus:ring-indigo-500" />
                    </div>
                  </div>

                  <button type="submit" disabled={isGenerating} id="btn-concoct-twister" className="w-full py-3 bg-slate-900 hover:bg-indigo-700 text-white font-bold text-xs uppercase tracking-widest rounded-sm shadow-md transition-all flex items-center justify-center gap-2 disabled:bg-slate-300">
                    {isGenerating ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    <span>{isGenerating ? "GENERATING CHALLENGE..." : "GENERATE LINGUISTIC CHALLENGE"}</span>
                  </button>
                </form>
              </div>

              <div className="lg:col-span-5 space-y-6">
                <div className="bg-white rounded-md border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 pb-1 border-b border-slate-100">Lately Concocted</h3>
                  <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
                    {isLoadingTwisters ? (
                      <div className="py-8 text-center text-xs text-slate-400 animate-pulse">Loading library logs...</div>
                    ) : twisters.length > 0 ? (
                      twisters.slice(0, 4).map((t) => (
                        <div key={t.id} className="p-3.5 rounded-sm border border-slate-200 bg-slate-50/50 flex flex-col justify-between gap-2.5">
                          <div>
                            <div className="flex gap-2 mb-1.5">
                              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-sm bg-indigo-50 text-indigo-700 uppercase">{t.difficulty}</span>
                              <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded-sm bg-slate-100 text-slate-500">{t.language}</span>
                            </div>
                            <p className="text-xs font-serif font-semibold italic text-slate-800">"{t.text}"</p>
                            {t.transliteration && t.transliteration !== t.text && (
                              <p className="text-[10px] font-mono text-indigo-600 mt-1">"{t.transliteration}"</p>
                            )}
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-slate-400 font-mono">Sound: {t.focusSound}</span>
                            <button onClick={() => { setSelectedTwister(t); setActiveTab('practice'); }} className="px-2.5 py-1 text-[10px] font-bold bg-indigo-600 hover:bg-indigo-700 text-white rounded-sm transition uppercase">Practice</button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="py-8 text-center text-xs text-slate-400">No custom twisters seeded yet.</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Vocal Arena */}
          {activeTab === 'practice' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-8">
                {selectedTwister ? (
                  <div className="bg-white rounded-md border border-slate-200 p-6 md:p-8 space-y-8">
                    <div className="bg-slate-50 rounded-sm p-6 md:p-8 border border-slate-200 flex flex-col justify-center items-center text-center">
                      <div className="flex items-center justify-between w-full mb-6 pb-2 border-b border-slate-200">
                        <span className="text-xs font-bold text-indigo-600 uppercase tracking-[0.2em]">Practice Target</span>
                        <button onClick={() => handleReadAloud(selectedTwister)} className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-600 transition font-bold uppercase tracking-wider">
                          <Volume2 className="w-4 h-4" />
                          <span>Quick Play</span>
                        </button>
                      </div>

                      {wordDiff.length > 0 ? (
                        <div className="flex flex-wrap justify-center gap-x-2 md:gap-x-3 gap-y-4 text-2xl font-serif font-medium italic text-slate-800 leading-relaxed max-w-3xl">
                          {wordDiff.map((item, idx) => {
                            if (item.status === 'correct') return <span key={idx} className="px-1.5 py-0.5 rounded-sm bg-emerald-50 text-emerald-800 border-b-2 border-emerald-500">{item.targetWord}</span>;
                            else if (item.status === 'partial') return (
                              <div key={idx} className="flex flex-col items-center">
                                <span className="px-1.5 py-0.5 rounded-sm bg-amber-50 text-amber-800 border-b-2 border-amber-500">{item.targetWord}</span>
                                <span className="text-[10px] not-italic font-mono text-amber-600 font-bold mt-1 px-1 bg-amber-50/50 rounded-xs">"{item.spokenWord}"</span>
                              </div>
                            );
                            else if (item.status === 'missed') return <span key={idx} className="px-1.5 py-0.5 rounded-sm bg-rose-50 text-rose-800 border-b-2 border-rose-400 line-through opacity-70">{item.targetWord}</span>;
                            return null;
                          })}
                        </div>
                      ) : (
                        <h3 className="text-2xl md:text-3xl font-serif font-medium italic text-slate-800 leading-relaxed max-w-3xl">"{selectedTwister.text}"</h3>
                      )}

                      {selectedTwister.transliteration && selectedTwister.transliteration !== selectedTwister.text && (
                        <div className="mt-5 px-5 py-2 border border-dashed border-indigo-200 bg-indigo-50/20 rounded-md max-w-2xl">
                          <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest text-center mb-0.5">English Transliteration / Pronunciation Guide</p>
                          <p className="text-xs md:text-sm font-mono text-center font-medium text-indigo-900 leading-relaxed">
                            "{selectedTwister.transliteration}"
                          </p>
                        </div>
                      )}

                      <div className="mt-6 flex flex-wrap items-center gap-3">
                        <span className="px-3 py-1 bg-slate-200/50 text-slate-700 text-[10px] font-bold uppercase rounded-sm">{selectedTwister.language}</span>
                        <span className="px-3 py-1 bg-slate-200/50 text-slate-700 text-[10px] font-bold uppercase rounded-sm">{selectedTwister.category}</span>
                        <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-[10px] font-bold uppercase rounded-sm">Accent: /{selectedTwister.focusSound}/</span>
                      </div>

                      {/* Voice Guide Controls Panel */}
                      <div className="mt-6 w-full max-w-2xl bg-white border border-slate-200 rounded p-4 text-left shadow-xs">
                        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-2.5 mb-3">
                          <div className="flex items-center gap-1.5 text-indigo-600">
                            <Volume2 className="w-4.5 h-4.5" />
                            <span className="text-xs font-extrabold uppercase tracking-widest">Acoustic Voice Guide Controls</span>
                          </div>
                          <span className="text-[9px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono font-bold uppercase">
                            Selected Voice: {ttsVoiceType === 'bold_indian' ? '🎙️ Indian Male Bold Voice' : '🌐 Native Accented Voice'}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {/* Voice Accent Preference Selector */}
                          <div className="space-y-1">
                            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Accent Voice</span>
                            <div className="flex bg-slate-100 p-0.5 rounded-sm">
                              <button
                                type="button"
                                onClick={() => {
                                  setTtsVoiceType('bold_indian');
                                  // Auto switch target to transliteration if available for non-English
                                  if (selectedTwister.transliteration && selectedTwister.transliteration !== selectedTwister.text) {
                                    setTtsSourceType('transliteration');
                                  }
                                }}
                                className={`flex-1 text-center py-1 text-[10px] font-bold uppercase rounded-xs transition-all ${
                                  ttsVoiceType === 'bold_indian' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800'
                                }`}
                              >
                                Indian Male
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  setTtsVoiceType('native');
                                  setTtsSourceType('text');
                                }}
                                className={`flex-1 text-center py-1 text-[10px] font-bold uppercase rounded-xs transition-all ${
                                  ttsVoiceType === 'native' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800'
                                }`}
                              >
                                Native Speak
                              </button>
                            </div>
                          </div>

                          {/* Speech Source Selector */}
                          <div className="space-y-1">
                            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Speech Target</span>
                            <div className="flex bg-slate-100 p-0.5 rounded-sm">
                              <button
                                type="button"
                                onClick={() => setTtsSourceType('transliteration')}
                                disabled={!selectedTwister.transliteration || selectedTwister.transliteration === selectedTwister.text}
                                className={`flex-1 text-center py-1 text-[10px] font-bold uppercase rounded-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                                  ttsSourceType === 'transliteration' && selectedTwister.transliteration && selectedTwister.transliteration !== selectedTwister.text
                                    ? 'bg-indigo-600 text-white shadow-xs'
                                    : 'text-slate-500 hover:text-slate-800'
                                }`}
                              >
                                Phonetic Guide
                              </button>
                              <button
                                type="button"
                                onClick={() => setTtsSourceType('text')}
                                className={`flex-1 text-center py-1 text-[10px] font-bold uppercase rounded-xs transition-all ${
                                  ttsSourceType === 'text' || !selectedTwister.transliteration || selectedTwister.transliteration === selectedTwister.text
                                    ? 'bg-indigo-600 text-white shadow-xs'
                                    : 'text-slate-500 hover:text-slate-800'
                                }`}
                              >
                                Native Text
                              </button>
                            </div>
                          </div>

                          {/* Speech Speed/Tempo Option Selector */}
                          <div className="space-y-1">
                            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Playback Tempo</span>
                            <div className="flex bg-slate-100 p-0.5 rounded-sm">
                              {[
                                { label: 'Slower', val: 0.60 },
                                { label: 'Medium', val: 0.75 },
                                { label: 'Normal', val: 0.95 }
                              ].map((opt) => (
                                <button
                                  type="button"
                                  key={opt.val}
                                  onClick={() => setTtsSpeed(opt.val)}
                                  className={`flex-1 text-center py-1 text-[10px] font-bold uppercase rounded-xs transition-all ${
                                    ttsSpeed === opt.val ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800'
                                  }`}
                                >
                                  {opt.label}
                                </button>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="mt-3.5 flex gap-2">
                          <button
                            type="button"
                            onClick={() => handleReadAloud(selectedTwister)}
                            className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-extrabold uppercase tracking-widest rounded-sm flex items-center justify-center gap-2 shadow-xs transition-all"
                          >
                            <Volume2 className="w-4 h-4" />
                            <span>Speak Practice Guide</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => window.speechSynthesis.cancel()}
                            className="px-4 py-2.5 border border-slate-200 text-slate-500 hover:bg-slate-50 text-[11px] font-bold uppercase tracking-wider rounded-sm transition-all"
                          >
                            Stop
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className="border border-slate-200 rounded-sm p-6 flex flex-col items-center justify-center space-y-4">
                      {manualMode ? (
                        <form onSubmit={handleManualSubmit} className="w-full max-w-xl space-y-3">
                          <div className="flex items-center justify-between">
                            <label className="text-xs font-bold text-slate-400 uppercase tracking-widest">Type spoken attempt</label>
                            <button type="button" onClick={() => setManualMode(false)} className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider">Use Mic</button>
                          </div>
                          <div className="flex gap-2">
                            <input type="text" value={manualInput} onChange={(e) => setManualInput(e.target.value)} placeholder="Type exactly what you said..." className="flex-1 border border-slate-200 p-3 rounded-sm text-xs outline-none focus:ring-1 focus:ring-indigo-500" />
                            <button type="submit" className="px-4 py-3 bg-slate-900 text-white font-bold text-xs uppercase tracking-wider rounded-sm">Analyze</button>
                          </div>
                        </form>
                      ) : (
                        <div className="flex flex-col items-center space-y-4 w-full">
                          <div className="flex items-center gap-4">
                            {!isRecording ? (
                              <button onClick={startSpeechRecognition} className="w-16 h-16 rounded-full bg-slate-900 text-white flex items-center justify-center hover:bg-indigo-600 transition-all shadow-md active:scale-95">
                                <Mic className="w-6 h-6" />
                              </button>
                            ) : (
                              <button onClick={stopRecording} className="w-16 h-16 rounded-full bg-rose-600 text-white flex items-center justify-center hover:bg-rose-700 transition-all shadow-lg animate-pulse">
                                <Square className="w-6 h-6 fill-current" />
                              </button>
                            )}
                          </div>
                          <h4 className="text-sm font-bold text-slate-800">{isRecording ? "Listening... Speak now!" : "Click mic to start practice"}</h4>
                          <button onClick={() => setManualMode(true)} className="text-[10px] text-slate-500 hover:text-indigo-600 font-bold uppercase tracking-wider">Manual Keyboard Mode</button>
                        </div>
                      )}

                      {isAnalyzing && (
                        <div className="text-center py-2 flex items-center gap-2 text-indigo-600 font-bold text-xs uppercase tracking-widest animate-pulse">
                          <RotateCcw className="w-4 h-4 animate-spin" />
                          <span>Python Aligner Parsing Sounds...</span>
                        </div>
                      )}
                    </div>

                    {accuracy !== null && wpm !== null && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                        <div className="border border-slate-200 rounded-sm p-6 space-y-6">
                          <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider border-b border-slate-100 pb-2">Your Performance</h4>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-50 p-4 border border-slate-200 rounded-sm text-center">
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Accuracy</span>
                              <h3 className="text-3xl font-extrabold text-emerald-600">{accuracy}%</h3>
                            </div>
                            <div className="bg-slate-50 p-4 border border-slate-200 rounded-sm text-center">
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Tempo</span>
                              <h3 className="text-3xl font-extrabold text-indigo-600">{wpm} WPM</h3>
                            </div>
                          </div>

                          {coachInsights && (
                            <div className="bg-gradient-to-br from-indigo-50/50 to-purple-50/30 border border-indigo-100 rounded-sm p-5 space-y-4">
                              <span className="text-[10px] font-extrabold text-indigo-900 uppercase tracking-wider block">AI Phonetic Coach Feedback</span>
                              <p className="text-xs text-slate-600 font-medium leading-relaxed">{coachInsights.diagnosis}</p>
                              <div className="bg-white border border-indigo-100 p-3 rounded-sm">
                                <span className="text-[9px] font-bold text-indigo-500 uppercase block mb-0.5">Warm-up Drill</span>
                                <p className="text-xs font-serif font-semibold italic text-slate-800">"{coachInsights.warmUpDrill}"</p>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="border border-slate-200 rounded-sm p-6 space-y-4">
                          <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider border-b border-slate-100 pb-2">Acoustic Alignments</h4>
                          <div className="space-y-2.5 max-h-[250px] overflow-y-auto pr-1">
                            {wordDiff.map((item, idx) => {
                              if (item.status === 'correct') return null;
                              return (
                                <div key={idx} className={`p-3 rounded-sm border flex items-center justify-between text-xs ${item.status === 'partial' ? 'bg-amber-50/30 border-amber-200' : 'bg-rose-50/20 border-rose-200'}`}>
                                  <div>
                                    <span className="text-[9px] font-bold uppercase block text-slate-400">{item.status}</span>
                                    <span className="font-semibold">{item.status === 'partial' ? `Expected "${item.targetWord}", heard "${item.spokenWord}"` : `Skipped "${item.targetWord}"`}</span>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        <div className="md:col-span-2 flex justify-end pt-2">
                          <button onClick={handleSaveAttempt} disabled={saveStatus === 'saving' || saveStatus === 'saved'} className="px-6 py-3 bg-slate-900 hover:bg-indigo-700 text-white rounded-sm font-bold text-xs uppercase tracking-widest transition-all">
                            {saveStatus === 'saving' ? "LOGGING..." : saveStatus === 'saved' ? "SAVED!" : "LOG PRACTICE ATTEMPT"}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-white rounded-md border border-slate-200 p-8 text-center flex flex-col items-center justify-center min-h-[350px]">
                    <Mic className="w-10 h-10 text-indigo-600 mb-3" />
                    <h3 className="text-lg font-bold text-slate-800">No Target Challenge Selected</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-sm">Pick any challenge from the right-hand panel to start practicing.</p>
                  </div>
                )}
              </div>

              <div className="lg:col-span-4 bg-white rounded-md border border-slate-200 p-6 shadow-sm h-fit">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4">Target Library Catalog</h3>
                <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
                  {twisters.map((t) => (
                    <button key={t.id} onClick={() => setSelectedTwister(t)} className={`w-full text-left p-3 rounded-sm border text-xs transition flex flex-col gap-1.5 ${selectedTwister?.id === t.id ? 'border-indigo-600 bg-indigo-50/50' : 'border-slate-100 hover:bg-slate-50'}`}>
                      <div className="flex items-center justify-between w-full">
                        <span className="font-semibold text-slate-800 line-clamp-1">"{t.text}"</span>
                        <span className="text-[8px] font-bold uppercase px-1 rounded bg-slate-100">{t.difficulty}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Library */}
          {activeTab === 'directory' && (
            <div className="space-y-6">
              <div className="bg-white p-5 border border-slate-200 rounded-sm shadow-sm flex flex-col md:flex-row items-center gap-3 justify-between">
                <div className="relative w-full md:w-80">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search tongue twisters..." className="w-full bg-slate-50 border border-slate-200 rounded-sm py-2 pl-10 pr-4 text-xs outline-none focus:ring-1 focus:ring-indigo-500" />
                </div>
                <div className="flex flex-wrap gap-2 w-full md:w-auto">
                  <select value={langFilter} onChange={(e) => setLangFilter(e.target.value)} className="bg-slate-50 border border-slate-200 rounded-sm py-2 px-3 text-xs font-semibold text-slate-600 outline-none">
                    <option value="All">🌍 All Languages</option>
                    {uniqueLangs.filter(l => l !== 'All').map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                  <select value={diffFilter} onChange={(e) => setDiffFilter(e.target.value)} className="bg-slate-50 border border-slate-200 rounded-sm py-2 px-3 text-xs font-semibold text-slate-600 outline-none">
                    <option value="All">🔥 All Difficulties</option>
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {filteredTwisters.map((t) => (
                  <div key={t.id} className="bg-white border border-slate-200 rounded-sm p-6 flex flex-col justify-between">
                    <div>
                      <div className="flex gap-2 mb-3">
                        <span className="text-[9px] font-bold uppercase bg-slate-100 text-slate-600 px-2 py-0.5 rounded-sm">{t.language}</span>
                        <span className="text-[9px] font-bold uppercase bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-sm">{t.difficulty}</span>
                      </div>
                      <h3 className="text-lg font-serif italic font-medium text-slate-800 leading-snug mb-2">"{t.text}"</h3>
                      {t.transliteration && t.transliteration !== t.text && (
                        <div className="mb-4 p-2.5 bg-indigo-50/20 border border-dashed border-indigo-100 rounded text-slate-600 font-mono text-xs">
                          <span className="text-[9px] font-sans font-extrabold uppercase text-indigo-400 tracking-wider block mb-0.5">Transliteration</span>
                          "{t.transliteration}"
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between items-center border-t border-slate-100 pt-4 mt-4">
                      <button onClick={() => handleLike(t.id)} className="flex items-center gap-1 text-xs text-slate-400 hover:text-rose-500">
                        <Heart className="w-4 h-4 text-rose-500" />
                        <span>{t.likes}</span>
                      </button>
                      <button onClick={() => { setSelectedTwister(t); setActiveTab('practice'); }} className="px-3 py-1.5 bg-slate-950 text-white font-bold text-[10px] uppercase rounded-sm hover:bg-indigo-700 transition">Practice</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Diagnostics */}
          {activeTab === 'dashboard' && stats && (
            <div className="space-y-8">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-sm border border-slate-200 shadow-sm flex items-center gap-4">
                  <div className="p-3 bg-indigo-50 text-indigo-600 rounded-sm"><BookOpen className="w-5 h-5" /></div>
                  <div>
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block">Total Twisters</span>
                    <span className="text-xl font-bold block">{stats.totalGenerated}</span>
                  </div>
                </div>
                <div className="bg-white p-5 rounded-sm border border-slate-200 shadow-sm flex items-center gap-4">
                  <div className="p-3 bg-violet-50 text-violet-600 rounded-sm"><Activity className="w-5 h-5" /></div>
                  <div>
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block">Vocal Runs</span>
                    <span className="text-xl font-bold block">{stats.totalAttempts}</span>
                  </div>
                </div>
                <div className="bg-white p-5 rounded-sm border border-slate-200 shadow-sm flex items-center gap-4">
                  <div className="p-3 bg-emerald-50 text-emerald-600 rounded-sm"><Award className="w-5 h-5" /></div>
                  <div>
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block">Avg Accuracy</span>
                    <span className="text-xl font-bold text-emerald-600 block">{stats.averageAccuracy}%</span>
                  </div>
                </div>
                <div className="bg-white p-5 rounded-sm border border-slate-200 shadow-sm flex items-center gap-4">
                  <div className="p-3 bg-amber-50 text-amber-600 rounded-sm"><Flame className="w-5 h-5 animate-pulse" /></div>
                  <div>
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block">Daily Streak</span>
                    <span className="text-xl font-bold text-amber-600 block">{stats.practiceStreak} Days</span>
                  </div>
                </div>
              </div>

              {/* Progress Charts */}
              <div className="bg-white rounded-md border border-slate-200 p-6 shadow-sm">
                <h3 className="text-sm font-bold text-slate-800 uppercase mb-4">Vocal Pronunciation Progression</h3>
                <div className="h-[250px] w-full">
                  {stats.progressData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={stats.progressData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="date" stroke="#94a3b8" fontSize={9} />
                        <YAxis stroke="#4f46e5" fontSize={9} />
                        <Tooltip />
                        <Area type="monotone" dataKey="accuracy" name="Accuracy %" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.05} />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full flex items-center justify-center bg-slate-50 border border-slate-100 rounded-sm">
                      <span className="text-xs text-slate-400 font-bold uppercase">Log attempts to populate timeline charts!</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Python diagnostic report */}
              <div className="bg-white rounded-md border border-slate-200 p-6 shadow-sm">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                      <Award className="w-5 h-5 text-indigo-600" />
                      <span>Vocal Coach Diagnostic Report</span>
                    </h3>
                    <p className="text-xs text-slate-400 font-medium mt-0.5">Compiled dynamically by our custom Python Speech Diagnostics engine</p>
                  </div>
                  <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-[9px] font-extrabold uppercase rounded-sm tracking-wider">Python Powered</span>
                </div>

                {isReportLoading ? (
                  <div className="py-8 text-center text-xs text-slate-400 animate-pulse font-bold uppercase tracking-wider">
                    Evaluating oral history and compiling diagnostic logs...
                  </div>
                ) : reportText ? (
                  <div className="bg-slate-50 border border-slate-200/80 rounded-sm p-5 font-mono text-xs text-slate-700 overflow-x-auto whitespace-pre-wrap leading-relaxed shadow-inner">
                    {reportText}
                  </div>
                ) : (
                  <div className="py-8 text-center text-xs text-slate-400 font-bold uppercase tracking-wider">
                    No diagnostic insights compiled. Record a session to populate report logs.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="h-12 border-t border-slate-200 bg-white flex items-center justify-between px-6 md:px-8 text-xs text-slate-500 shrink-0">
        <span>© {new Date().getFullYear()} Twist.ai. All rights reserved.</span>
        <span>Acoustic Speech Training</span>
      </footer>
    </div>
  );
}
