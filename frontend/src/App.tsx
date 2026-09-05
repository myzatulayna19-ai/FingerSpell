import React, { useState } from 'react';
import { ActiveTab, UserStats, Lesson, Achievement } from './types';
import { INITIAL_LESSONS, INITIAL_ACHIEVEMENTS } from './data';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { Lessons } from './components/Lessons';
import { Dictionary } from './components/Dictionary';
import { ProgressReport } from './components/ProgressReport';
import { motion, AnimatePresence } from 'motion/react';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  
  // Track global learning milestones statefully
  const [stats, setStats] = useState<UserStats>({
    streak: 12,
    xp: 2450,
    signsLearned: 38,
    perfectFormsPercent: 78,
    weeklyMinutes: 25,
    goalMinutes: 40,
    overallMastery: 68
  });

  const [lessons] = useState<Lesson[]>(INITIAL_LESSONS);
  const [currentLessonIdx, setCurrentLessonIdx] = useState<number>(0);
  const [bookmarks, setBookmarks] = useState<string[]>(['dict_hello']);
  const [achievements, setAchievements] = useState<Achievement[]>(INITIAL_ACHIEVEMENTS);

  const currentLesson = lessons[currentLessonIdx];

  // Increase experience metrics on successful sign validation
  const handleUpdateStats = (xpGain: number) => {
    setStats(prev => {
      const nextXp = prev.xp + xpGain;
      const nextSigns = prev.signsLearned + 1;
      const nextMinutes = prev.weeklyMinutes + 5;
      const nextMastery = Math.min(100, Math.floor(prev.overallMastery + 1));
      
      // Update award lists statefully if boundaries are crossed
      if (nextSigns >= 40) {
        setAchievements(curr => 
          curr.map(ach => ach.id === 'quick_learner' ? { ...ach, unlocked: true, unlockedAt: new Date().toISOString().split('T')[0] } : ach)
        );
      }
      return {
        ...prev,
        xp: nextXp,
        signsLearned: nextSigns,
        weeklyMinutes: nextMinutes,
        overallMastery: nextMastery
      };
    });
  };

  const handleNextLesson = () => {
    setCurrentLessonIdx((prev) => (prev + 1) % lessons.length);
  };

  const handleToggleBookmark = (wordId: string) => {
    setBookmarks(prev => 
      prev.includes(wordId) 
        ? prev.filter(id => id !== wordId) 
        : [...prev, wordId]
    );
  };

  // Map requested views
  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard 
            stats={stats} 
            currentLesson={currentLesson} 
            startLesson={() => setActiveTab('lessons')} 
            setActiveTab={setActiveTab}
          />
        );
      case 'lessons':
        return (
          <Lessons 
            currentLesson={currentLesson}
            stats={stats}
            updateStats={handleUpdateStats}
            nextLesson={handleNextLesson}
          />
        );
      case 'dictionary':
        return (
          <Dictionary 
            bookmarks={bookmarks} 
            toggleBookmark={handleToggleBookmark}
          />
        );
      case 'progress':
        return (
          <ProgressReport 
            stats={stats} 
            achievements={achievements}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50 flex flex-col font-sans antialiased text-slate-800">
      
      {/* Platform Navigation */}
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        stats={stats} 
      />

      {/* Main Workspace Frame container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-20">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.16, ease: 'easeOut' }}
            className="w-full h-full"
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </main>

    </div>
  );
}
