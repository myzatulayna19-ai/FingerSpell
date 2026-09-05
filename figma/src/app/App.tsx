import { useEffect, useRef, useState } from "react";
import {
  Hand,
  Camera,
  BookOpen,
  CheckCircle,
  ChevronRight,
  Menu,
  X,
  Award,
  BarChart2,
  ArrowRight,
  Users,
  Zap,
  Volume2,
  RotateCcw,
  Star,
  TrendingUp,
  Clock,
  Target,
} from "lucide-react";

const signImageModules = (import.meta as any).glob(
  "./components/assets/signs/*.{jpg,jpeg,png,JPG,PNG}",
  { eager: true }
) as Record<string, { default: string }>;

const signImagesMap: Record<string, string> = {};

Object.entries(signImageModules).forEach(([path, mod]) => {
  const fileName = path.split("/").pop()?.split(".")[0];
  if (fileName) {
    signImagesMap[fileName] = mod.default;
  }
});

const getSignImageUrl = (signName: string) => {
  return signImagesMap[signName] || "";
};

type Tab = "home" | "alphabets" | "greetings" | "practice" | "progress";

const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

const GREETINGS = [
  { malay: "Selamat Pagi", english: "Good Morning", category: "time" },
  { malay: "Selamat Petang", english: "Good Afternoon", category: "time" },
  { malay: "Selamat Malam", english: "Good Evening", category: "time" },
  { malay: "Apa Khabar?", english: "How Are You?", category: "social" },
  { malay: "Khabar Baik", english: "I Am Fine", category: "social" },
  { malay: "Terima Kasih", english: "Thank You", category: "courtesy" },
  { malay: "Sama-sama", english: "You're Welcome", category: "courtesy" },
  { malay: "Maaf", english: "Sorry / Excuse Me", category: "courtesy" },
  { malay: "Ya", english: "Yes", category: "basic" },
  { malay: "Tidak", english: "No", category: "basic" },
  { malay: "Tolong", english: "Please / Help", category: "basic" },
  { malay: "Nama saya...", english: "My name is...", category: "intro" },
  { malay: "Selamat tinggal", english: "Goodbye", category: "farewell" },
  { malay: "Jumpa lagi", english: "See You Again", category: "farewell" },
  { malay: "Sihat?", english: "Are You Well?", category: "social" },
  { malay: "Sila masuk", english: "Please Come In", category: "courtesy" },
];

const PROGRESS_DATA = [
  { label: "A–F", done: 6, total: 6 },
  { label: "G–L", done: 4, total: 6 },
  { label: "M–R", done: 2, total: 6 },
  { label: "S–Z", done: 0, total: 8 },
];

const CATEGORY_COLORS: Record<string, string> = {
  time: "bg-blue-50 text-blue-700 border-blue-200",
  social: "bg-emerald-50 text-emerald-700 border-emerald-200",
  courtesy: "bg-amber-50 text-amber-700 border-amber-200",
  basic: "bg-violet-50 text-violet-700 border-violet-200",
  intro: "bg-rose-50 text-rose-700 border-rose-200",
  farewell: "bg-teal-50 text-teal-700 border-teal-200",
};


function Nav({ tab, setTab, menuOpen, setMenuOpen }: {
  tab: Tab;
  setTab: (t: Tab) => void;
  menuOpen: boolean;
  setMenuOpen: (v: boolean) => void;
}) {
  const links: { id: Tab; label: string }[] = [
    { id: "home", label: "Home" },
    { id: "alphabets", label: "Alphabets" },
    { id: "greetings", label: "Greetings" },
    { id: "practice", label: "Practice" },
    { id: "progress", label: "Progress" },
  ];

  return (
    <nav
      className="sticky top-0 z-50 bg-background border-b border-border"
      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-16">
        <button
          onClick={() => setTab("home")}
          className="flex items-center gap-2.5 group"
        >
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Hand className="w-4 h-4 text-white" strokeWidth={2.5} />
          </div>
          <span className="font-bold text-base text-foreground tracking-tight">
            BIM<span className="text-accent">·</span>Belajar
          </span>
        </button>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {links.map((l) => (
            <button
              key={l.id}
              onClick={() => setTab(l.id)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                tab === l.id
                  ? "bg-secondary text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          <button className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Log In
          </button>
          <button
            onClick={() => setTab("practice")}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
          >
            Try Gesture Cam
          </button>
        </div>

        <button
          className="md:hidden p-2 text-foreground"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden border-t border-border bg-background px-6 pb-4 flex flex-col gap-1">
          {links.map((l) => (
            <button
              key={l.id}
              onClick={() => { setTab(l.id); setMenuOpen(false); }}
              className={`text-left px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                tab === l.id
                  ? "bg-secondary text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      )}
    </nav>
  );
}

function HomePage({ setTab }: { setTab: (t: Tab) => void }) {
  return (
    <div style={{ fontFamily: "'DM Sans', sans-serif" }}>
      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-16 pb-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary border border-border text-xs font-semibold text-primary mb-6 tracking-wide uppercase"
            style={{ fontFamily: "'DM Mono', monospace" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-accent inline-block"></span>
            Bahasa Isyarat Malaysia
          </div>
          <h1
            className="text-5xl font-extrabold text-foreground leading-[1.1] mb-5 tracking-tight"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Learn Sign Language<br />
            <span className="text-primary">with Your Hands.</span>
          </h1>
          <p className="text-lg text-muted-foreground leading-relaxed mb-8 max-w-md">
            Master all 26 BIM alphabets and essential daily greetings through real-time gesture
            tracking. Your webcam is your teacher.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setTab("alphabets")}
              className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:opacity-90 transition-opacity"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Start Learning <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setTab("practice")}
              className="flex items-center gap-2 px-6 py-3 border border-border rounded-lg text-foreground font-semibold hover:bg-muted transition-colors"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              <Camera className="w-4 h-4" /> Try Gesture Cam
            </button>
          </div>

          <div className="flex items-center gap-6 mt-10 pt-8 border-t border-border">
            {[
              { value: "26", label: "Alphabets" },
              { value: "16+", label: "Greetings" },
              { value: "Free", label: "Forever" },
            ].map((s) => (
              <div key={s.label}>
                <div
                  className="text-2xl font-bold text-foreground"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {s.value}
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Hero visual */}
        <div className="relative">
          <div className="aspect-[4/3] rounded-2xl bg-secondary overflow-hidden border border-border relative flex flex-col">
            {/* Simulated webcam frame */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-48 h-56 relative">
                {/* Hand silhouette suggestion */}
                <div className="w-full h-full flex items-center justify-center">
                  <Hand className="w-32 h-32 text-primary opacity-20" strokeWidth={1} />
                </div>
                {/* Tracking dots */}
                {[
                  { top: "20%", left: "50%" },
                  { top: "35%", left: "30%" },
                  { top: "35%", left: "70%" },
                  { top: "55%", left: "25%" },
                  { top: "55%", left: "75%" },
                  { top: "70%", left: "35%" },
                  { top: "70%", left: "65%" },
                  { top: "80%", left: "50%" },
                ].map((pos, i) => (
                  <div
                    key={i}
                    className="absolute w-2.5 h-2.5 rounded-full bg-accent border-2 border-white shadow-md"
                    style={{ top: pos.top, left: pos.left, transform: "translate(-50%,-50%)" }}
                  />
                ))}
              </div>
            </div>

            {/* Top bar */}
            <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-4 py-3 bg-gradient-to-b from-white/80 to-transparent">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-400"></div>
                <div className="w-2 h-2 rounded-full bg-amber-400"></div>
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
              </div>
              <div className="text-xs font-medium text-muted-foreground"
                style={{ fontFamily: "'DM Mono', monospace" }}>
                GESTURE CAM — LIVE
              </div>
            </div>

            {/* Bottom detection overlay */}
            <div className="absolute bottom-0 left-0 right-0 px-4 py-3 bg-gradient-to-t from-white/90 to-transparent">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs text-muted-foreground mb-0.5"
                    style={{ fontFamily: "'DM Mono', monospace" }}>
                    DETECTED
                  </div>
                  <div
                    className="text-3xl font-extrabold text-primary leading-none"
                    style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                  >
                    A
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-muted-foreground mb-1">Confidence</div>
                  <div className="w-24 h-2 bg-border rounded-full overflow-hidden">
                    <div className="w-[92%] h-full bg-accent rounded-full"></div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1 text-right"
                    style={{ fontFamily: "'DM Mono', monospace" }}>
                    92%
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Floating badge */}
          <div className="absolute -bottom-4 -left-4 bg-white border border-border rounded-xl px-4 py-3 shadow-lg flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Today's streak</div>
              <div className="text-sm font-bold text-foreground"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                7 days 🔥
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature strip */}
      <section className="bg-muted border-y border-border py-14">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: <Camera className="w-5 h-5" />,
                title: "Real-Time Gesture Tracking",
                desc: "Your webcam detects hand landmarks live and scores each gesture against reference BIM signs.",
                color: "bg-primary text-white",
              },
              {
                icon: <BookOpen className="w-5 h-5" />,
                title: "Full Alphabet Library",
                desc: "All 26 letters of the BIM alphabet with step-by-step handshape guides and reference images.",
                color: "bg-accent text-accent-foreground",
              },
              {
                icon: <Users className="w-5 h-5" />,
                title: "Daily Greetings & Phrases",
                desc: "16 essential BIM greetings used in everyday Malaysian life — from Selamat Pagi to Terima Kasih.",
                color: "bg-emerald-600 text-white",
              },
            ].map((f) => (
              <div
                key={f.title}
                className="bg-background rounded-xl border border-border p-6 hover:shadow-md transition-shadow"
              >
                <div className={`w-10 h-10 rounded-lg ${f.color} flex items-center justify-center mb-4`}>
                  {f.icon}
                </div>
                <h3
                  className="font-bold text-base text-foreground mb-2"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {f.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="text-xs font-semibold text-muted-foreground tracking-widest uppercase mb-4"
              style={{ fontFamily: "'DM Mono', monospace" }}>
              How It Works
            </div>
            <h2
              className="text-3xl font-extrabold text-foreground mb-10 leading-tight"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Three steps to sign language fluency
            </h2>
            <div className="flex flex-col gap-8">
              {[
                {
                  n: "01",
                  title: "Choose a Lesson",
                  desc: "Pick from alphabets A–Z or any of the 16 greeting phrases. Each lesson shows the correct BIM handshape.",
                },
                {
                  n: "02",
                  title: "Mimic the Sign",
                  desc: "Enable your webcam and hold up the sign. Our model tracks 21 hand landmarks to score your gesture in real time.",
                },
                {
                  n: "03",
                  title: "Track Your Progress",
                  desc: "Each correct sign is logged to your progress dashboard. Earn streaks and review what needs more practice.",
                },
              ].map((step) => (
                <div key={step.n} className="flex gap-5">
                  <div
                    className="text-4xl font-extrabold text-border shrink-0 w-12 text-right leading-none mt-1"
                    style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                  >
                    {step.n}
                  </div>
                  <div>
                    <div
                      className="font-bold text-base text-foreground mb-1"
                      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                    >
                      {step.title}
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick lesson preview grid */}
          <div className="grid grid-cols-2 gap-4">
            {["A", "B", "C", "D"].map((letter) => (
              <div
                key={letter}
                className="aspect-square rounded-xl bg-secondary border border-border flex flex-col items-center justify-center gap-3 hover:border-primary transition-colors cursor-pointer group"
              >
                <div className="w-16 h-16 rounded-full bg-background border border-border flex items-center justify-center">
                  <Hand className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" strokeWidth={1.5} />
                </div>
                <div
                  className="text-4xl font-extrabold text-primary"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {letter}
                </div>
                <div className="text-xs text-muted-foreground">BIM Sign</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="bg-primary mx-6 mb-16 rounded-2xl overflow-hidden">
        <div className="max-w-6xl mx-auto px-10 py-14 flex flex-col md:flex-row items-center justify-between gap-8">
          <div>
            <h2
              className="text-2xl font-extrabold text-white mb-2"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Ready to communicate in BIM?
            </h2>
            <p className="text-white/70 text-sm max-w-md">
              Join thousands of Malaysians learning to bridge the communication gap. Start free, stay free.
            </p>
          </div>
          <div className="flex gap-3 shrink-0">
            <button
              onClick={() => setTab("alphabets")}
              className="px-6 py-3 bg-accent text-accent-foreground rounded-lg font-bold text-sm hover:opacity-90 transition-opacity"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Start with Alphabets
            </button>
            <button
              onClick={() => setTab("greetings")}
              className="px-6 py-3 bg-white/10 text-white rounded-lg font-bold text-sm border border-white/20 hover:bg-white/20 transition-colors"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Learn Greetings
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

function AlphabetsPage({ 
  setTab,
  masteredLetters,
}: { 
  setTab: (t: Tab) => void; 
  masteredLetters: Set<string>;
}) {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="max-w-6xl mx-auto px-6 py-12" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <div className="flex items-start justify-between mb-10">
        <div>
          <div className="text-xs font-semibold text-muted-foreground tracking-widest uppercase mb-3"
            style={{ fontFamily: "'DM Mono', monospace" }}>
            Module 1 of 2
          </div>
          <h1
            className="text-4xl font-extrabold text-foreground mb-3"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            BIM Alphabets
          </h1>
          <p className="text-muted-foreground max-w-md">
            All 26 letters of the Bahasa Isyarat Malaysia alphabet. Select any letter to see the reference handshape and practice with gesture tracking.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-2 bg-muted rounded-xl px-4 py-3 border border-border">
          <Award className="w-4 h-4 text-accent" />
          <span className="text-sm font-semibold text-foreground"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            10 / 26 mastered
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-muted-foreground">Overall progress</span>
          <span className="text-xs font-semibold text-foreground"
            style={{ fontFamily: "'DM Mono', monospace" }}>
            38%
          </span>
        </div>
        <div className="h-2 bg-border rounded-full overflow-hidden">
          <div className="h-full w-[38%] bg-primary rounded-full"></div>
        </div>
      </div>

      {/* Alphabet grid */}
      <div className="grid grid-cols-5 sm:grid-cols-7 md:grid-cols-9 gap-3 mb-10">
        {ALPHABET.map((letter) => {
          const mastered = masteredLetters.has(letter);
          const isSelected = selected === letter;
          return (
            <button
              key={letter}
              onClick={() => setSelected(isSelected ? null : letter)}
              className={`aspect-square rounded-xl border-2 flex flex-col items-center justify-center gap-1 transition-all font-bold text-lg
                ${isSelected
                  ? "border-primary bg-primary text-white scale-105 shadow-lg"
                  : mastered
                  ? "border-emerald-300 bg-emerald-50 text-emerald-700 hover:border-emerald-400"
                  : "border-border bg-card text-foreground hover:border-primary hover:bg-secondary"
                }`}
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              {letter}
              {mastered && !isSelected && (
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Selected letter panel */}
      {selected && (
        <div className="bg-secondary border border-border rounded-2xl p-6 mb-8 grid md:grid-cols-3 gap-6 items-start">
          {/* Reference panel */}
          <div className="aspect-square bg-background rounded-xl border border-border flex flex-col items-center justify-center gap-3">
            <Hand className="w-20 h-20 text-primary opacity-30" strokeWidth={1} />
            <div
              className="text-5xl font-extrabold text-primary"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              {selected}
            </div>
            <div className="text-xs text-muted-foreground">Reference Handshape</div>
          </div>

          {/* Instructions */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <span
                  className="text-white font-extrabold text-lg"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {selected}
                </span>
              </div>
              <div>
                <h3
                  className="font-bold text-xl text-foreground"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  Letter {selected}
                </h3>
                <div className="text-xs text-muted-foreground">BIM Manual Alphabet</div>
              </div>
              {masteredLetters.has(selected) && (
                <div className="ml-auto flex items-center gap-1.5 px-3 py-1 bg-emerald-100 rounded-full">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-xs font-semibold text-emerald-700">Mastered</span>
                </div>
              )}
            </div>

            <div className="flex flex-col gap-2 mb-6">
              {[
                "Position your dominant hand at chest height.",
                "Form the handshape shown in the reference image.",
                "Keep your wrist neutral — no extreme bends.",
                "Hold still for 1 second for the camera to detect.",
              ].map((tip, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div
                    className="shrink-0 w-5 h-5 rounded-full bg-primary text-white text-xs flex items-center justify-center font-bold mt-0.5"
                    style={{ fontFamily: "'DM Mono', monospace" }}
                  >
                    {i + 1}
                  </div>
                  <p className="text-sm text-muted-foreground">{tip}</p>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setTab("practice")}
                className="flex items-center gap-2 px-5 py-2.5 bg-primary text-white rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                <Camera className="w-4 h-4" /> Practice Now
              </button>
              <button className="flex items-center gap-2 px-5 py-2.5 border border-border rounded-lg text-sm font-semibold hover:bg-muted transition-colors">
                <Volume2 className="w-4 h-4" /> Pronunciation
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Group breakdown */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {PROGRESS_DATA.map((g) => (
          <div key={g.label} className="bg-card border border-border rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span
                className="font-bold text-sm text-foreground"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {g.label}
              </span>
              <span
                className="text-xs text-muted-foreground"
                style={{ fontFamily: "'DM Mono', monospace" }}
              >
                {g.done}/{g.total}
              </span>
            </div>
            <div className="h-1.5 bg-border rounded-full overflow-hidden">
              <div
                className="h-full bg-primary rounded-full"
                style={{ width: `${(g.done / g.total) * 100}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GreetingsPage({ setTab }: { setTab: (t: Tab) => void }) {
  const [filter, setFilter] = useState<string>("all");

  const categories = ["all", "time", "social", "courtesy", "basic", "intro", "farewell"];
  const filtered = filter === "all" ? GREETINGS : GREETINGS.filter((g) => g.category === filter);

  return (
    <div className="max-w-6xl mx-auto px-6 py-12" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <div className="mb-10">
        <div className="text-xs font-semibold text-muted-foreground tracking-widest uppercase mb-3"
          style={{ fontFamily: "'DM Mono', monospace" }}>
          Module 2 of 2
        </div>
        <h1
          className="text-4xl font-extrabold text-foreground mb-3"
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          Basic Greetings
        </h1>
        <p className="text-muted-foreground max-w-lg">
          16 everyday BIM phrases grouped by context. Practice each sign with the gesture camera to unlock it.
        </p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            className={`px-4 py-1.5 rounded-full border text-sm font-medium capitalize transition-colors ${
              filter === c
                ? "bg-primary text-white border-primary"
                : "border-border text-muted-foreground hover:text-foreground hover:border-foreground/30"
            }`}
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            {c}
          </button>
        ))}
      </div>

      {/* Greetings grid */}
      <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-12">
        {filtered.map((g, i) => (
          <div
            key={g.malay}
            className="group bg-card border border-border rounded-xl overflow-hidden hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
          >
            {/* Handshape placeholder */}
            <div className="aspect-[4/3] bg-secondary flex items-center justify-center relative">
              <Hand
                className="w-14 h-14 text-primary opacity-20 group-hover:opacity-40 transition-opacity"
                strokeWidth={1}
              />
              <div
                className="absolute bottom-3 right-3 text-xs font-semibold text-muted-foreground border border-border rounded-md px-2 py-0.5 bg-background"
                style={{ fontFamily: "'DM Mono', monospace" }}
              >
                {String(i + 1).padStart(2, "0")}
              </div>
            </div>

            <div className="p-4">
              <div className="flex items-start justify-between mb-1">
                <h3
                  className="font-bold text-base text-foreground leading-tight"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {g.malay}
                </h3>
              </div>
              <p className="text-sm text-muted-foreground mb-3">{g.english}</p>
              <div className="flex items-center justify-between">
                <span
                  className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border capitalize ${
                    CATEGORY_COLORS[g.category] ?? "bg-muted text-muted-foreground border-border"
                  }`}
                >
                  {g.category}
                </span>
                <button
                  onClick={() => setTab("practice")}
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-primary hover:bg-secondary transition-colors"
                >
                  <Camera className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Practice CTA */}
      <div className="flex items-center justify-between bg-secondary border border-border rounded-2xl px-8 py-6">
        <div>
          <h3
            className="font-bold text-lg text-foreground mb-1"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Ready to practice a greeting?
          </h3>
          <p className="text-sm text-muted-foreground">Enable your webcam and start signing.</p>
        </div>
        <button
          onClick={() => setTab("practice")}
          className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg font-bold text-sm hover:opacity-90 transition-opacity shrink-0"
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          Open Gesture Cam <Camera className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

Object.entries(signImageModules).forEach(([path, mod]) => {
  const fileName = path.split("/").pop()?.split(".")[0];
  if (fileName) {
    signImagesMap[fileName] = mod.default;
  }
});


function PracticePage({
  masteredLetters,
  setMasteredLetters,
}: {
  masteredLetters: Set<string>;
  setMasteredLetters: React.Dispatch<React.SetStateAction<Set<string>>>;
}) {
  const [camEnabled, setCamEnabled] = useState(false);
  const [mode, setMode] = useState<"alphabet" | "greeting">("alphabet");
  const [currentSign, setCurrentSign] = useState("A");
  const [score, setScore] = useState(0);
  const [status, setStatus] = useState("");
  const [feedback, setFeedback] = useState<string[]>([]);
  const [detectedGesture, setDetectedGesture] = useState("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startCameraStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 800 },
        },
        audio: false,
      });

      streamRef.current = stream;
      setCamEnabled(true);
    } catch (err) {
      console.error("Camera activation failed:", err);
      alert("Unable to access camera. Please allow camera permission.");
      setCamEnabled(false);
    }
  };

  const stopCameraStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCamEnabled(false);
    setScore(0);
  };

  useEffect(() => {
    if (camEnabled && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;

      videoRef.current.play().catch((error) => {
        console.error("Video play error:", error);
      });
    }
  }, [camEnabled]);

  const isProcessingRef = useRef(false);

  const sendFrameToBackend = async (targetSign: string) => {
    if (isProcessingRef.current) return;
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA || video.videoWidth === 0) {
      return;
    }

    isProcessingRef.current = true;

    try {
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      if (!context) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const imageData = canvas.toDataURL("image/jpeg", 0.8);

      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image: imageData,
          target: targetSign,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();
      const newScore = Number(data.accuracy) || 0;

      setScore(newScore);
      setStatus(data.status ?? "");
      setDetectedGesture(data.gesture ?? "");
      setFeedback(Array.isArray(data.feedback) ? data.feedback : []);

      if (newScore >= 100) {
        setMasteredLetters((prev) => new Set(prev).add(targetSign));
      }
    } catch (error) {
      console.error("Recognition request failed:", error);
    } finally {
      isProcessingRef.current = false;
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      sendFrameToBackend(currentSign);
    }, 1000);

    return () => clearInterval(interval);
  }, [currentSign]);

  const signs = mode === "alphabet" ? ALPHABET : GREETINGS.map((g) => g.malay);

  return (
    <div className="max-w-6xl mx-auto px-6 py-12" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <div className="mb-8">
        <div
          className="text-xs font-semibold text-muted-foreground tracking-widest uppercase mb-3"
          style={{ fontFamily: "'DM Mono', monospace" }}
        >
          Interactive Practice
        </div>
        <h1
          className="text-4xl font-extrabold text-foreground mb-3"
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          Gesture Camera
        </h1>
        <p className="text-muted-foreground max-w-lg">
          Allow camera access, face the sign at your webcam, and get instant feedback on your handshape accuracy.
        </p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-1 bg-muted border border-border rounded-xl p-1 w-fit mb-8">
        {(["alphabet", "greeting"] as const).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setCurrentSign(m === "alphabet" ? "A" : GREETINGS[0].malay);
            }}
            className={`px-5 py-2 rounded-lg text-sm font-semibold capitalize transition-colors ${
              mode === m ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            }`}
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            {m === "alphabet" ? "Alphabets" : "Greetings"}
          </button>
        ))}
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Camera feed */}
        <div className="md:col-span-2">
          <div
            className={`rounded-2xl border-2 overflow-hidden relative ${
              camEnabled ? "border-primary" : "border-dashed border-border"
            }`}
            style={{ aspectRatio: "4/3" }}
          >
            {camEnabled ? (
              <div className="w-full h-full bg-black relative">
                {/* Status & Feedback */}
                {status && (
                  <div className="absolute top-10 left-4 right-4 z-10">
                    <div className="bg-white/95 rounded-xl px-4 py-3 shadow-lg">
                      <div className="font-semibold text-lg">
                        {status === "Correct" ? "✓" : "✕"} {status}
                      </div>

                      {feedback.length > 0 && (
                        <div className="text-sm text-gray-600 mt-1">{feedback[0]}</div>
                      )}
                    </div>
                  </div>
                )}

                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                <canvas ref={canvasRef} width={640} height={480} className="hidden" />

                {/* Corner tracking indicators */}
                {["top-3 left-3", "top-3 right-3", "bottom-3 left-3", "bottom-3 right-3"].map((pos) => (
                  <div key={pos} className={`absolute ${pos}`}>
                    <div className="w-5 h-5 border-2 border-accent rounded-sm opacity-60"></div>
                  </div>
                ))}

                {/* Live badge */}
                <div
                  className="absolute top-2 left-4 flex items-center gap-2 bg-black/50 text-white text-xs px-3 py-1.5 rounded-full backdrop-blur-sm"
                  style={{ fontFamily: "'DM Mono', monospace" }}
                >
                  <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse"></div>
                  LIVE
                </div>

                {/* Confidence meter */}
                <div className="absolute bottom-4 left-4 right-4 bg-black/40 backdrop-blur-sm rounded-xl px-4 py-3 text-white">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs opacity-70">Alphabet Sign</span>
                    <span className="text-xs opacity-70" style={{ fontFamily: "'DM Mono', monospace" }}>
                      Accuracy: {score}%
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div
                      className="text-4xl font-extrabold text-accent"
                      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                    >
                      {currentSign}
                    </div>
                    <div className="flex-1 h-2 bg-white/20 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent rounded-full transition-all"
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center gap-4 bg-muted">
                <div className="w-16 h-16 rounded-2xl bg-background border border-border flex items-center justify-center">
                  <Camera className="w-7 h-7 text-muted-foreground" />
                </div>
                <div className="text-center">
                  <h3
                    className="font-bold text-base text-foreground mb-1"
                    style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                  >
                    Camera not enabled
                  </h3>
                  <p className="text-sm text-muted-foreground max-w-xs">
                    Allow access to your webcam to start gesture recognition.
                  </p>
                </div>
                <button
                  onClick={startCameraStream}
                  className="mt-2 px-6 py-2.5 bg-primary text-white rounded-lg text-sm font-bold hover:opacity-90 transition-opacity"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  Enable Camera
                </button>
              </div>
            )}
          </div>

          {camEnabled && (
            <div className="flex gap-3 mt-4">
              <button
                onClick={stopCameraStream}
                className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                <X className="w-4 h-4" /> Disable Camera
              </button>
              <button className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors">
                <RotateCcw className="w-4 h-4" /> Reset
              </button>
            </div>
          )}
        </div>

        {/* Right column (Target Preview + Sign Selector) */}
        <div className="flex flex-col gap-4">
          <div className="bg-card border border-border rounded-xl p-5">
            <h3
              className="font-bold text-sm text-foreground mb-1"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Current Target
            </h3>
            <div className="text-xs text-muted-foreground mb-4">Sign this to score points</div>

            <div className="aspect-square bg-secondary rounded-xl flex items-center justify-center relative overflow-hidden p-4 border border-border">
              {getSignImageUrl(currentSign) ? (
                <img
                  key={currentSign}
                  src={getSignImageUrl(currentSign)}
                  alt={`Sign for ${currentSign}`}
                  className="w-full h-full object-contain rounded-lg"
                />
              ) : (
                <div className="text-center text-muted-foreground text-sm">
                  Image for <span className="font-bold text-foreground">{currentSign}</span> not found
                </div>
              )}

              <div
                className="absolute bottom-3 right-3 bg-primary text-primary-foreground font-extrabold text-lg px-3 py-1 rounded-lg shadow-md"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {currentSign}
              </div>
            </div>
          </div>

          {/* Sign List */}
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-border">
              <h3
                className="font-bold text-sm text-foreground"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {mode === "alphabet" ? "All Letters" : "All Greetings"}
              </h3>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {signs.map((s) => (
                <button
                  key={s}
                  onClick={() => setCurrentSign(s)}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-sm border-b border-border last:border-0 hover:bg-muted transition-colors ${
                    currentSign === s ? "bg-secondary text-primary font-semibold" : "text-foreground"
                  }`}
                  style={{ fontFamily: currentSign === s ? "'Plus Jakarta Sans', sans-serif" : undefined }}
                >
                  <span>{s}</span>
                  {masteredLetters.has(s) && <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProgressPage({masteredLetters}: {masteredLetters: Set<string>}) {
  const completedCount = masteredLetters.size;
  const greetingsDone = 4;

  return (
    <div className="max-w-6xl mx-auto px-6 py-12" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <div className="mb-10">
        <div className="text-xs font-semibold text-muted-foreground tracking-widest uppercase mb-3"
          style={{ fontFamily: "'DM Mono', monospace" }}>
          Your Journey
        </div>
        <h1
          className="text-4xl font-extrabold text-foreground mb-3"
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          Progress Dashboard
        </h1>
        <p className="text-muted-foreground">Track your mastery across BIM alphabets and greetings.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { icon: <Award className="w-5 h-5" />, label: "Alphabets Mastered", value: `${completedCount}/26`, color: "text-primary", bg: "bg-blue-50" },
          { icon: <Star className="w-5 h-5" />, label: "Greetings Learned", value: `${greetingsDone}/16`, color: "text-amber-600", bg: "bg-amber-50" },
          { icon: <TrendingUp className="w-5 h-5" />, label: "Current Streak", value: "7 days", color: "text-emerald-600", bg: "bg-emerald-50" },
          { icon: <Clock className="w-5 h-5" />, label: "Time Practiced", value: "3h 22m", color: "text-violet-600", bg: "bg-violet-50" },
        ].map((s) => (
          <div key={s.label} className="bg-card border border-border rounded-xl p-5">
            <div className={`w-9 h-9 rounded-lg ${s.bg} flex items-center justify-center mb-3 ${s.color}`}>
              {s.icon}
            </div>
            <div
              className="text-2xl font-extrabold text-foreground mb-1"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              {s.value}
            </div>
            <div className="text-xs text-muted-foreground">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Alphabet mastery grid */}
      <div className="bg-card border border-border rounded-2xl p-6 mb-6">
        <h2
          className="font-bold text-base text-foreground mb-5"
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          Alphabet Mastery
        </h2>
        <div className="grid grid-cols-6 sm:grid-cols-[repeat(13,minmax(0,1fr))] gap-2">
          {ALPHABET.map((letter) => {
            const mastered = masteredLetters.has(letter);
            return (
              <div
                key={letter}
                className={`aspect-square rounded-lg flex items-center justify-center text-sm font-bold border transition-colors ${
                  mastered
                    ? "bg-primary text-white border-primary"
                    : "bg-muted text-muted-foreground border-border"
                }`}
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {letter}
              </div>
            );
          })}
        </div>
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-primary"></div>
            <span className="text-xs text-muted-foreground">Mastered ({completedCount})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-muted border border-border"></div>
            <span className="text-xs text-muted-foreground">Not yet ({26 - completedCount})</span>
          </div>
        </div>
      </div>

      {/* Greetings progress */}
      <div className="bg-card border border-border rounded-2xl p-6 mb-6">
        <h2
          className="font-bold text-base text-foreground mb-5"
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          Greetings Progress
        </h2>
        <div className="flex flex-col gap-3">
          {GREETINGS.slice(0, 8).map((g, i) => {
            const done = i < greetingsDone;
            return (
              <div key={g.malay} className="flex items-center gap-4">
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                  done ? "bg-primary border-primary" : "border-border"
                }`}>
                  {done && <CheckCircle className="w-3 h-3 text-white" strokeWidth={3} />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${done ? "text-foreground" : "text-muted-foreground"}`}
                      style={{ fontFamily: done ? "'Plus Jakarta Sans', sans-serif" : undefined }}>
                      {g.malay}
                    </span>
                    <span className="text-xs text-muted-foreground">{g.english}</span>
                  </div>
                  <div className="h-1 bg-border rounded-full mt-1.5 overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: done ? "100%" : i === greetingsDone ? "45%" : "0%" }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Weekly activity */}
      <div className="bg-card border border-border rounded-2xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h2
            className="font-bold text-base text-foreground"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Weekly Activity
          </h2>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground"
            style={{ fontFamily: "'DM Mono', monospace" }}>
            <BarChart2 className="w-3.5 h-3.5" />
            Signs practiced
          </div>
        </div>
        <div className="flex items-end gap-2 h-24">
          {[
            { day: "Mon", count: 8 },
            { day: "Tue", count: 14 },
            { day: "Wed", count: 5 },
            { day: "Thu", count: 19 },
            { day: "Fri", count: 11 },
            { day: "Sat", count: 22 },
            { day: "Sun", count: 7 },
          ].map((d) => (
            <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full rounded-t-md bg-primary/20 hover:bg-primary/40 transition-colors relative group"
                style={{ height: `${(d.count / 22) * 80}px` }}
              >
                <div
                  className="absolute -top-5 left-1/2 -translate-x-1/2 text-xs font-semibold text-primary opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap"
                  style={{ fontFamily: "'DM Mono', monospace" }}
                >
                  {d.count}
                </div>
              </div>
              <span className="text-xs text-muted-foreground">{d.day}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Footer({ setTab }: { setTab: (t: Tab) => void }) {
  return (
    <footer
      className="border-t border-border bg-muted mt-12"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >
      <div className="max-w-6xl mx-auto px-6 py-12 grid md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Hand className="w-4 h-4 text-white" strokeWidth={2.5} />
            </div>
            <span
              className="font-bold text-base text-foreground"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              BIM<span className="text-accent">·</span>Belajar
            </span>
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Free, interactive Bahasa Isyarat Malaysia learning — for every Malaysian.
          </p>
        </div>

        {[
          {
            title: "Learn",
            links: [
              { label: "Alphabets", tab: "alphabets" as Tab },
              { label: "Greetings", tab: "greetings" as Tab },
              { label: "Practice", tab: "practice" as Tab },
            ],
          },
          {
            title: "Track",
            links: [
              { label: "My Progress", tab: "progress" as Tab },
            ],
          },
          {
            title: "About",
            links: [],
          },
        ].map((col) => (
          <div key={col.title}>
            <h4
              className="font-bold text-xs uppercase tracking-wider text-muted-foreground mb-3"
              style={{ fontFamily: "'DM Mono', monospace" }}
            >
              {col.title}
            </h4>
            <div className="flex flex-col gap-2">
              {col.links.map((l) => (
                <button
                  key={l.label}
                  onClick={() => setTab(l.tab)}
                  className="text-sm text-left text-muted-foreground hover:text-foreground transition-colors"
                >
                  {l.label}
                </button>
              ))}
              {col.title === "About" && (
                <>
                  <span className="text-sm text-muted-foreground">What is BIM?</span>
                  <span className="text-sm text-muted-foreground">Deaf Malaysia</span>
                  <span className="text-sm text-muted-foreground">Accessibility</span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-border">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            © 2025 BIM·Belajar. Made in Malaysia 🇲🇾
          </span>
          <div className="flex items-center gap-1 text-xs text-muted-foreground"
            style={{ fontFamily: "'DM Mono', monospace" }}>
            <Zap className="w-3.5 h-3.5 text-accent" />
            Powered by MediaPipe
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [menuOpen, setMenuOpen] = useState(false);
  const [masteredLetters, setMasteredLetters] = useState<Set<string>>(new Set());

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav tab={tab} setTab={setTab} menuOpen={menuOpen} setMenuOpen={setMenuOpen} />
      <main className="flex-1">
        {tab === "home" && <HomePage setTab={setTab} />}
        {tab === "alphabets" && (
          <AlphabetsPage setTab={setTab} masteredLetters={masteredLetters} />
        )}        
        {tab === "greetings" && <GreetingsPage setTab={setTab} />}
        {tab === "practice" && (<PracticePage
          masteredLetters={masteredLetters}
          setMasteredLetters={setMasteredLetters}
        />)}
        {tab === "progress" && (<ProgressPage 
          masteredLetters={masteredLetters}
        />)}
      </main>
      <Footer setTab={setTab} />
    </div>
  );
}
