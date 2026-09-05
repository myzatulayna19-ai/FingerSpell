import React, { useState } from 'react';
import { UserStats, Lesson } from '../types';
import { Play, Sparkles, Flame, Users, CheckCircle2, ChevronRight, Video, Target, Award } from 'lucide-react';

interface DashboardProps {
  stats: UserStats;
  currentLesson: Lesson;
  startLesson: () => void;
  setActiveTab: (tab: 'dashboard' | 'lessons' | 'dictionary' | 'progress') => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ stats, currentLesson, startLesson, setActiveTab }) => {
  const [showCommunityModal, setShowCommunityModal] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [joinedSuccess, setJoinedSuccess] = useState(false);

  // Group practice categories helper
  const categories = [
    { title: 'Basics & Greetings', progress: 100, count: '12 / 12 Signs', color: 'from-emerald-500 to-green-500', icon: '👋' },
    { title: 'BIM Alphabet', progress: 45, count: '11 / 26 Signs', color: 'from-blue-500 to-cyan-500', icon: '🔤' },
    { title: 'Family & Care', progress: 12, count: '2 / 15 Signs', color: 'from-amber-500 to-orange-500', icon: '🏠' },
    { title: 'Deaf Culture Phrases', progress: 0, count: '0 / 20 Signs', color: 'from-indigo-500 to-violet-500', icon: '💬' },
  ];

  const handleJoinSession = () => {
    setIsJoining(true);
    setTimeout(() => {
      setIsJoining(false);
      setJoinedSuccess(true);
    }, 1800);
  };

  return (
    <div id="dashboard-view" className="space-y-6">
      
      {/* Welcome Banner Card */}
      <div id="welcome-banner" className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-700 to-indigo-800 p-6 text-white shadow-xl shadow-blue-950/10 sm:p-8">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 h-64 w-64 rounded-full bg-blue-600/20 blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 -mb-12 h-40 w-44 rounded-full bg-indigo-500/10 blur-2xl"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-500/30 px-3 py-1 font-sans text-xs font-bold ring-1 ring-blue-400/20">
                <Sparkles className="h-3 w-3 text-blue-200 fill-current" />
                Beginner Track
              </span>
            </div>
            <h1 className="font-sans text-2xl font-extrabold tracking-tight sm:text-3xl">
              Welcome to FingerSpell! 👋
            </h1>
            <p className="max-w-xl font-sans text-sm text-blue-100 leading-relaxed">
              Start practicing Bahasa Isyarat Malaysia (BIM) today. Complete just <strong className="text-semibold text-white">one lesson</strong> to improve your gesture accuracy and receive real-time guidance feedback.
            </p>
          </div>
          <div className="flex shrink-0">
            <button
              id="dashboard-continue-learning-btn"
              onClick={startLesson}
              className="flex items-center gap-2 rounded-xl bg-white px-5 py-3.5 font-sans text-sm font-bold text-blue-700 shadow-md transition-all hover:-translate-y-0.5 hover:bg-blue-50 cursor-pointer"
            >
              <Play className="h-4 w-4 fill-current text-blue-700" />
              Start Lesson
            </button>
          </div>
        </div>
      </div>

      {/* Bento Grid Layout Section */}
      <div id="bento-grid-dashboard" className="grid gap-6 md:grid-cols-3">
        
        {/* Card 1: Active Progress Tracker Card */}
        <div id="bento-current-lesson" className="group relative overflow-hidden rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition-all hover:shadow-md md:col-span-2">
          <div className="absolute top-0 right-0 h-full w-48 bg-cover bg-right opacity-[0.03] transition-all group-hover:opacity-[0.06] pointer-events-none" style={{ backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuDbBE6D9VGGgYHtu14s0aw9sSj7t5-YpvmWitkWVpVwC8Lt8rmPbRnTuxBML6IcPG3bh_EGeKD_ZYAb7FQdMR_kGZwYB7QET8i5vNL7cWu9sBwMQC2uBPjMGm53MT8amEtxQ_s2REeLmPPjNVZHcVINgkC15rQ8CrF2ECDF-q-_ycZvgE6JTtOX-lv4wsWS4aIRPEbod6zpJ0uJtm17Rum_oec9PcRLg1hWwgElvI6Y53HKHPD8WHIurHV9tlQgFPA09JGv6hWdVO4')` }}></div>
          
          <div className="flex flex-col h-full justify-between gap-5">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-600">Current Objective</span>
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                  <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                  Active
                </span>
              </div>
              <h3 className="mt-2.5 font-sans text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                {currentLesson.title}
              </h3>
              <p className="mt-1 font-sans text-xs text-slate-500">
                Instructional Step: {currentLesson.instruction}
              </p>

              {/* Progress Slider Bar */}
              <div className="mt-5 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-700">Lesson Progress</span>
                  <span className="font-bold text-blue-600">{currentLesson.progress}% Complete</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div 
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500" 
                    style={{ width: `${currentLesson.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-50">
              <span className="text-xs font-medium text-slate-400">Award Count: +{currentLesson.xpReward} XP upon success</span>
              <button
                onClick={startLesson}
                className="flex items-center gap-1 font-sans text-xs font-bold text-blue-600 hover:text-blue-800 group/link cursor-pointer"
              >
                Resume Workspace
                <ChevronRight className="h-3.5 w-3.5 transition-all group-hover/link:translate-x-0.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Card 2: Weekly Circular Metrics Badge */}
        <div id="bento-weekly-goal" className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex flex-col h-full justify-between items-center text-center">
            <div className="w-full flex items-center justify-between border-b border-slate-50 pb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Weekly Goal</span>
              <Target className="h-4 w-4 text-slate-400" />
            </div>

            {/* Circular Progress Wheel */}
            <div className="relative my-4 flex h-28 w-28 items-center justify-center">
              <svg className="h-full w-full -rotate-90">
                <circle 
                  cx="56" 
                  cy="56" 
                  r="48" 
                  className="stroke-slate-100 fill-none" 
                  strokeWidth="8"
                />
                <circle 
                  cx="56" 
                  cy="56" 
                  r="48" 
                  className="stroke-blue-600 fill-none" 
                  strokeWidth="8"
                  strokeDasharray={`${2 * Math.PI * 48}`}
                  strokeDashoffset={`${2 * Math.PI * 48 * (1 - stats.weeklyMinutes / stats.goalMinutes)}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="font-sans text-2xl font-extrabold text-slate-900">{Math.round((stats.weeklyMinutes / stats.goalMinutes) * 100)}%</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Goal</span>
              </div>
            </div>

            <div className="text-sm">
              <p className="font-sans font-bold text-slate-800">
                {stats.weeklyMinutes} of {stats.goalMinutes} Minutes
              </p>
              <p className="font-sans text-xs text-slate-400 mt-1">
                Keep learning daily to maintain high streak
              </p>
            </div>
          </div>
        </div>

      </div>

      {/* Grid of Sub-Category Mastery Progress */}
      <div id="category-section" className="space-y-3">
        <h2 className="font-sans text-base font-bold text-slate-900 flex items-center gap-2">
          <span>Active Learning Categories</span>
          <span className="text-xs font-normal text-slate-400">({categories.length} segments total)</span>
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {categories.map((c, idx) => (
            <div key={idx} className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-sm space-y-3 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xl">{c.icon}</span>
                <span className="text-[10px] font-bold text-slate-400 font-mono">{c.count}</span>
              </div>
              <div>
                <h4 className="font-sans text-sm font-bold text-slate-800 leading-tight">{c.title}</h4>
                <div className="mt-3 flex items-center gap-2">
                  <div className="h-1.5 w-full rounded-full bg-slate-50 overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500" style={{ width: `${c.progress}%` }}></div>
                  </div>
                  <span className="text-xs font-black text-slate-600 font-mono min-w-[32px] text-right">{c.progress}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Peer Practice and Hangout Community Container */}
      <div id="community-hangout-section" className="overflow-hidden rounded-2xl border border-slate-100 bg-gradient-to-br from-indigo-50 to-blue-50 p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center lg:text-left">
            <div className="inline-flex items-center gap-1.5 rounded-full bg-indigo-100 px-3 py-1 font-sans text-xs font-bold text-indigo-800">
              <Users className="h-3.5 w-3.5" />
              Live Group Practice
            </div>
            <h3 className="font-sans text-lg font-bold text-slate-900">
              Community Hangout: BIM Greetings Cafe
            </h3>
            <p className="max-w-2xl font-sans text-xs text-slate-600 leading-relaxed">
              Skip solitary practice! Connect with 4 fellow Deaf and hearing learners currently online. Turn on your cameras to fingerspell together, peer-review gestural forms, and double your active practice times.
            </p>

            {/* Active peer avatars */}
            <div className="flex items-center justify-center lg:justify-start gap-1 pt-2">
              <div className="flex -space-x-2.5 overflow-hidden">
                <img
                  className="inline-block h-7 w-7 rounded-full object-cover ring-2 ring-white"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCM_Abpehoxo3N4NMYaO0qo_xuAGyNStdLNXqvJ14-HxdZnKr64TXoGltkIJV_cjkkoUMZYHwYCm6n2E51S6N1AEaJzdFRjpWLK1AlajbMxII2NE148ZUOvm518fHGJCeCDojeqW4lAf2PNVH7UzWbv64lsnc_wxNXXd9hXrryOjFuo-11eshIOH-38xx9PO16s12dkqYA6qL2tftslDES-zHhTGuIq4WT8N4UQ3a7WBzVis6AdGvBN_Iq-3xjcn_AtnyNUetV5M4rs"
                  alt="Stafford profile avatar"
                />
                <img
                  className="inline-block h-7 w-7 rounded-full object-cover ring-2 ring-white"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuDO1OLJMyNuscShWaorswjSemivUTenkgmgoEcax3vZcJpB-ulPdyV0aE7y7bCOpSon1xa1RE3_ei2WQXvrAFA0VXl2WJJ78MFRFwqhH51ujItDF_kw-LZsuex0siqH32sXvDN_0OGidZapkLYydHLSZrZcUoZSLtDWu5BFXoFOopduR6jVAZ8muB10nNS-O4NGqWZeraUZTFeGsHbDLBLgDiupRHtMsEXoaazLHx_CFh78Bi-DV-HYFugncRAMd2Mf4zRhVplPTXJ6"
                  alt="Gavin avatar"
                />
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-200 text-[10px] font-bold text-slate-600 ring-2 ring-white font-mono">
                  +3
                </div>
              </div>
              <span className="text-[11px] text-slate-500 font-semibold ml-1.5">Stafford, Gavin, and 3 others are signing now</span>
            </div>
          </div>

          <div className="shrink-0">
            <button
              id="join-hangout-btn"
              onClick={() => setShowCommunityModal(true)}
              className="flex items-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-sans text-xs font-bold px-4.5 py-3 shadow-md shadow-blue-500/10 cursor-pointer"
            >
              <Video className="h-4 w-4" />
              Join Cafe Lounge
            </button>
          </div>
        </div>
      </div>

      {/* Community Hangout Modal Interface */}
      {showCommunityModal && (
        <div id="community-modal" className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 animate-fade-in backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl relative">
            <button 
              onClick={() => { setShowCommunityModal(false); setJoinedSuccess(false); }} 
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 font-bold cursor-pointer"
            >
              ✕
            </button>
            <h3 className="font-sans text-lg font-extrabold text-slate-900 flex items-center gap-2">
              🤟 Greetings Cafe Lounge
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-500">
              Prepare to sign live in our peer-learning lounge. Standard expectations are friendly expressions, camera-enabled setups, and zero voice-noise (signing-only sandbox!).
            </p>

            <div className="mt-5 rounded-xl border border-indigo-100 bg-indigo-50/50 p-4 flex flex-col items-center gap-3">
              <span className="text-2xl">👥</span>
              <div className="text-center">
                <span className="text-xs font-extrabold text-indigo-900 block">Social Practice: Sign Hangout #104</span>
                <span className="text-[10px] text-indigo-600 font-medium font-mono">Active latency: healthy | 5 connected</span>
              </div>
            </div>

            {joinedSuccess ? (
              <div className="mt-6 space-y-4 text-center">
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-lg text-xs font-bold">
                  🎉 Connection Established! Joining feed...
                </div>
                <button
                  onClick={() => { setShowCommunityModal(false); setJoinedSuccess(false); setActiveTab('lessons'); }}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white font-sans text-xs font-bold py-2.5 rounded-xl transition-all cursor-pointer"
                >
                  Enter Sign Workspace
                </button>
              </div>
            ) : (
              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() => setShowCommunityModal(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-100 rounded-lg cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleJoinSession}
                  disabled={isJoining}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-md transition-all cursor-pointer min-w-[120px]"
                >
                  {isJoining ? 'Connecting...' : 'Authorize Camera'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
