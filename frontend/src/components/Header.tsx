import React from 'react';
import { ActiveTab, UserStats } from '../types';
import { Flame, Star, Award, BookOpen, MessageSquare, BarChart2, Compass, Bell, CheckSquare } from 'lucide-react';

interface HeaderProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  stats: UserStats;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, stats }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-100 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Branding Logo */}
        <div id="logo-branding" className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 font-sans text-xl font-extrabold text-white shadow-md shadow-blue-500/20">
            🤟
          </div>
          <div>
            <span className="font-sans text-lg font-extrabold tracking-tight text-slate-900">FingerSpell</span>
          </div>
        </div>

        {/* Primary Tabs Navigation */}
        <nav id="header-nav-tabs" className="hidden md:flex items-center gap-1.5">
          <button
            id="tab-dashboard-btn"
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 font-sans text-sm font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-blue-50 text-blue-700 font-semibold'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            <Compass className="h-4.5 w-4.5" />
            Learn
          </button>

          <button
            id="tab-lessons-btn"
            onClick={() => setActiveTab('lessons')}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 font-sans text-sm font-medium transition-all ${
              activeTab === 'lessons'
                ? 'bg-blue-50 text-blue-700 font-semibold'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            <CheckSquare className="h-4.5 w-4.5" />
            Practice
          </button>

          <button
            id="tab-dictionary-btn"
            onClick={() => setActiveTab('dictionary')}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 font-sans text-sm font-medium transition-all ${
              activeTab === 'dictionary'
                ? 'bg-blue-50 text-blue-700 font-semibold'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            <BookOpen className="h-4.5 w-4.5" />
            Dictionary
          </button>

          <button
            id="tab-progress-btn"
            onClick={() => setActiveTab('progress')}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 font-sans text-sm font-medium transition-all ${
              activeTab === 'progress'
                ? 'bg-blue-50 text-blue-700 font-semibold'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            <BarChart2 className="h-4.5 w-4.5" />
            My Progress
          </button>
        </nav>

        {/* User Stats Pill Container */}
        <div id="header-user-status" className="flex items-center gap-3.5">
          
          {/* Dynamic Streak Meter */}
          <div id="stat-streak-badge" className="flex items-center gap-1 bg-amber-50 border border-amber-100 text-amber-700 px-2.5 py-1 rounded-full text-xs font-bold" title="Daily Practice Streak">
            <Flame className="h-3.5 w-3.5 fill-current animate-pulse text-amber-500" />
            <span>{stats.streak} Days</span>
          </div>

          {/* Dynamic XP Meter */}
          <div id="stat-xp-badge" className="flex items-center gap-1 bg-violet-50 border border-violet-100 text-violet-700 px-2.5 py-1 rounded-full text-xs font-bold" title="Rank Experience Points">
            <Star className="h-3.5 w-3.5 fill-current text-violet-500" />
            <span>{stats.xp} XP</span>
          </div>

          <div className="h-6 w-[1px] bg-slate-200 hidden sm:block"></div>

          {/* Notification Alert Bell */}
          <button id="notification-bell" className="relative p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-50 transition-all cursor-pointer">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 flex h-2 w-2 rounded-full bg-red-500"></span>
          </button>

          {/* Sarah Avatar / Mock Profile */}
          <div id="profile-container" className="flex items-center gap-2 cursor-pointer hover:opacity-90 select-none">
            <img
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDbgPllwOxr7C-Yzx5ruuN5oK-MvabP0bJN-cN-11sSQJYiCsdXnUgS4CyoxNEHEme0zmY_JrToaTVQXdEsJvCyyNGifHDs_S1MFhVxLAxalnhMNYCd40x4G1b52rgqxXCQSHc0ycunJH0ZzhkzJKs2LXoHz-Ttmkelo7ryAYUROwLGiH_0iJP_xmaseEfT3Jv0Kscfb9hjZFYciScNY7RX-t-aibZxfMDSYUG9OI8mDHahQFkY3KNEU2bsirV5oQv3a3CCVP7Z4Z-m"
              alt="Sarah Profile avatar"
              className="h-8.5 w-8.5 rounded-full object-cover border border-slate-200 ring-2 ring-blue-50/50"
            />
            <span className="hidden lg:block font-sans text-sm font-semibold text-slate-700">Sarah</span>
          </div>
        </div>
      </div>

      {/* Mobile Sticky Tab Navigation Footer */}
      <div className="md:hidden border-t border-slate-100 bg-white flex items-center justify-around py-2 px-1">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex flex-col items-center gap-1 text-[10px] font-medium transition-all ${
            activeTab === 'dashboard' ? 'text-blue-600' : 'text-slate-400'
          }`}
        >
          <Compass className="h-5 w-5" />
          Learn
        </button>
        <button
          onClick={() => setActiveTab('lessons')}
          className={`flex flex-col items-center gap-1 text-[10px] font-medium transition-all ${
            activeTab === 'lessons' ? 'text-blue-600' : 'text-slate-400'
          }`}
        >
          <CheckSquare className="h-5 w-5" />
          Practice
        </button>
        <button
          onClick={() => setActiveTab('dictionary')}
          className={`flex flex-col items-center gap-1 text-[10px] font-medium transition-all ${
            activeTab === 'dictionary' ? 'text-blue-600' : 'text-slate-400'
          }`}
        >
          <BookOpen className="h-5 w-5" />
          Dictionary
        </button>
        <button
          onClick={() => setActiveTab('progress')}
          className={`flex flex-col items-center gap-1 text-[10px] font-medium transition-all ${
            activeTab === 'progress' ? 'text-blue-600' : 'text-slate-400'
          }`}
        >
          <BarChart2 className="h-5 w-5" />
          Progress
        </button>
      </div>
    </header>
  );
};
