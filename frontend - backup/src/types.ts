export type ActiveTab = 'dashboard' | 'lessons' | 'dictionary' | 'progress';

export interface Lesson {
  id: string;
  title: string;
  category: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  instructorImage: string;
  instruction: string;
  description: string;
  progress: number; // percentage
  xpReward: number;
  tip: string;
  signPhrase: string; // text representing what's being signed
}

export interface DictionaryWord {
  id: string;
  phrase: string;
  category: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  imageUrl: string;
  summary: string;
  description?: string;
  handShape?: string;
  armMovement?: string;
  facialExpression?: string;
  fingerSpelling?: string[];
  culturalContext?: string;
  isBookmarked: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: string;
  followUpPrompts?: string[];
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  unlocked: boolean;
  unlockedAt?: string;
}

export interface UserStats {
  streak: number;
  xp: number;
  signsLearned: number;
  perfectFormsPercent: number;
  weeklyMinutes: number;
  goalMinutes: number;
  overallMastery: number;
}
