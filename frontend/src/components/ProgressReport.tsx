import React from 'react';
import { UserStats, Achievement } from '../types';
import { Award, Flame, Star, BookOpen, CheckSquare, Sparkles, TrendingUp, Calendar, AlertCircle } from 'lucide-react';

interface ProgressProps {
  stats: UserStats;
  achievements: Achievement[];
}

export const ProgressReport: React.FC<ProgressProps> = ({ stats, achievements }) => {
  // Mock weekly practice distribution data points
  const weeklyData = [
    { day: 'Mon', mins: 12 },
    { day: 'Tue', mins: 25 },
    { day: 'Wed', mins: 18 },
    { day: 'Thu', mins: 32 },
    { day: 'Fri', mins: 15 },
    { day: 'Sat', mins: 10 },
    { day: 'Sun', mins: 14 }
  ];

  const maxMins = 40; // baseline height ceiling

  return (
    <div id="progress-view" className="space-y-6">
      
      {/* Top Mastery Overview Card */}
      <div className="grid gap-6 md:grid-cols-4">
        
        {/* Card 1: Mastery Ring */}
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm flex flex-col justify-between md:col-span-1 text-center items-center">
          <div>
            <span className="text-[10px] font-extrabold text-blue-600 uppercase tracking-widest block font-mono">My Standing</span>
            <h3 className="font-sans text-sm font-extrabold text-slate-800 leading-none mt-1">Intermediate Learner</h3>
          </div>
          
          <div className="relative flex h-24 w-24 items-center justify-center my-3">
            <svg className="h-full w-full rotate-90 scale-x-[-1]">
              <circle cx="48" cy="48" r="40" className="stroke-slate-50 fill-none" strokeWidth="6"/>
              <circle 
                cx="48" 
                cy="48" 
                r="40" 
                className="stroke-blue-600 fill-none" 
                strokeWidth="6"
                strokeDasharray={`${2 * Math.PI * 40}`}
                strokeDashoffset={`${2 * Math.PI * 40 * (1 - stats.overallMastery / 100)}`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute text-center">
              <span className="font-sans text-xl font-black text-slate-900">{stats.overallMastery}%</span>
              <span className="text-[9px] text-slate-400 block font-bold leading-none uppercase">Mastery</span>
            </div>
          </div>
          
          <span className="text-[10px] text-slate-400 leading-tight">Master 50 more signs to rank up to Advanced Class</span>
        </div>

        {/* Card 2, 3, 4: Quick Metrics Bento Box */}
        <div className="md:col-span-3 grid gap-4 grid-cols-2 lg:grid-cols-3">
          
          <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-sm space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Practice Streak</span>
              <Flame className="h-4.5 w-4.5 text-orange-500 fill-current" />
            </div>
            <span className="font-sans text-2xl font-black text-slate-900 block leading-none">{stats.streak} Days</span>
            <span className="text-[10px] text-slate-400 block leading-normal">Last signed: Today at 02:57 UTC</span>
          </div>

          <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-sm space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Learning Score</span>
              <Star className="h-4.5 w-4.5 text-indigo-500 fill-current" />
            </div>
            <span className="font-sans text-2xl font-black text-slate-900 block leading-none">{stats.xp} XP</span>
            <span className="text-[10px] text-slate-400 block leading-normal">Level 4 Scholar • +350 XP this week</span>
          </div>

          <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-sm space-y-1.5 col-span-2 lg:col-span-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Verified Forms</span>
              <CheckSquare className="h-4.5 w-4.5 text-emerald-500" />
            </div>
            <span className="font-sans text-2xl font-black text-slate-900 block leading-none">{stats.perfectFormsPercent}% Perfect</span>
            <span className="text-[10px] text-slate-400 block leading-normal">Evaluated via AI hand tracking calibration</span>
          </div>

        </div>

      </div>

      {/* SVG-Based Weekly Activity Dashboard */}
      <div id="weekly-chart-report" className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-50 pb-3 mb-4">
          <div>
            <h3 className="font-sans text-sm font-extrabold text-slate-800 flex items-center gap-1.5">
              <TrendingUp className="h-4 w-4 text-blue-600" />
              Weekly Practice Distribution
            </h3>
            <span className="text-[10px] text-slate-400">Hours spent signing on camera per weekday</span>
          </div>
          <span className="inline-flex items-center gap-1 rounded bg-slate-50 border border-slate-100 px-2.5 py-1 text-[10px] font-bold text-slate-500">
            <Calendar className="h-3 w-3" />
            June 1 - June 7, 2026
          </span>
        </div>

        {/* Dynamic Vector Bar Graph */}
        <div className="w-full">
          <div className="h-36 flex items-end justify-between px-2 sm:px-6 relative border-b border-slate-100 pb-2">
            
            {/* Guide Lines */}
            <div className="absolute inset-x-0 top-1/4 border-t border-slate-50 border-dashed pointer-events-none"></div>
            <div className="absolute inset-x-0 top-2/4 border-t border-slate-50 border-dashed pointer-events-none"></div>
            <div className="absolute inset-x-0 top-3/4 border-t border-slate-50 border-dashed pointer-events-none"></div>

            {weeklyData.map((d, idx) => {
              const heightPercent = `${(d.mins / maxMins) * 100}%`;
              const isTargetDay = d.mins >= 25;
              return (
                <div key={idx} className="flex flex-col items-center flex-1 h-full justify-end group px-1">
                  {/* Floating marker on hover */}
                  <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[9px] font-bold py-1 px-1.5 rounded absolute -top-5 z-10 select-none font-mono mb-2">
                    {d.mins} min
                  </span>
                  {/* High chart bar */}
                  <div 
                    className={`w-full max-w-[28px] rounded-t-cl transition-all duration-300 relative ${
                      isTargetDay 
                        ? 'bg-gradient-to-t from-blue-600 to-indigo-500 hover:brightness-110 shadow shadow-blue-500/10' 
                        : 'bg-slate-200 hover:bg-slate-300'
                    }`}
                    style={{ height: heightPercent, borderRadius: '4px 4px 0 0' }}
                  ></div>
                  <span className="mt-2 text-[10px] font-black text-slate-400 font-mono tracking-wider block uppercase">
                    {d.day}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Unlocked Badges & Achievements List */}
      <div id="achievements-section" className="space-y-3.5">
        <h3 className="font-sans text-base font-bold text-slate-900 flex items-center gap-1.5">
          <Award className="h-4.5 w-4.5 text-blue-600" />
          Achievement Badges Unlocked
        </h3>
        
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {achievements.map((ach) => (
            <div 
              key={ach.id}
              className={`rounded-xl border p-4.5 flex gap-4 transition-all relative overflow-hidden ${
                ach.unlocked 
                  ? 'bg-white border-slate-100 shadow-sm' 
                  : 'bg-slate-50/50 border-slate-100/50 opacity-60'
              }`}
            >
              {/* Colored Ribbon accent */}
              <div className={`absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b ${ach.color}`}></div>
              
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-sans text-sm font-bold text-slate-800 leading-tight block">
                    {ach.title}
                  </h4>
                  {ach.unlocked && (
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest font-mono">
                      Unlocked
                    </span>
                  )}
                </div>
                <p className="font-sans text-[11px] text-slate-500 leading-normal">
                  {ach.description}
                </p>
                {ach.unlockedAt && (
                  <span className="text-[9px] font-semibold text-slate-400 block pt-1">
                    Earned: {ach.unlockedAt}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
