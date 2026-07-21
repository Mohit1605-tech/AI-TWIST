/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type DifficultyLevel = 'easy' | 'medium' | 'hard';

export interface TongueTwister {
  id: string;
  text: string;
  language: string;
  difficulty: DifficultyLevel;
  category: string;
  focusSound: string;
  meaning: string;
  transliteration?: string;
  originalPrompt?: string;
  likes: number;
  attemptCount: number;
  averageAccuracy?: number;
  createdAt: string;
}

export interface PracticeAttempt {
  id: string;
  twisterId: string;
  twisterText: string;
  spokenText: string;
  accuracy: number; // percentage 0-100
  wpm: number; // Words Per Minute
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
}

export function getPublicShareUrl(twisterId: string): string {
  return `${window.location.origin}${window.location.pathname}?t=${twisterId}`;
}

