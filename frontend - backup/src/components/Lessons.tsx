import React, { useState, useRef, useEffect } from 'react';
import { Lesson, UserStats } from '../types';
import { Camera, CheckSquare, Sparkles, RefreshCw, AlertCircle, ArrowRight, Play, Award, Volume2, ShieldAlert } from 'lucide-react';

interface LessonsProps {
  currentLesson: Lesson;
  stats: UserStats;
  updateStats: (xpGain: number) => void;
  nextLesson: () => void;
  prevLesson?: () => void;
}

export const Lessons: React.FC<LessonsProps> = ({ currentLesson, stats, updateStats, nextLesson }) => {
  const [useLiveCamera, setUseLiveCamera] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [practiceState, setPracticeState] = useState<'idle' | 'calibrating' | 'tracking' | 'success'>('idle');
  const [progressPercent, setProgressPercent] = useState(0);
  const [feedbackOverlay, setFeedbackOverlay] = useState<string>('');
  
  // Coordinates helper for the joint tracker lines
  const [skeletonJoints, setSkeletonJoints] = useState<{x: number, y: number}[]>([
    {x: 154, y: 190}, {x: 168, y: 172}, {x: 182, y: 154}, {x: 200, y: 140}, // Thumb
    {x: 146, y: 130}, {x: 152, y: 104}, {x: 158, y: 80},  // Index
    {x: 128, y: 122}, {x: 132, y: 92},  {x: 136, y: 68},  // Middle
    {x: 110, y: 128}, {x: 112, y: 100}, {x: 114, y: 78},  // Ring
    {x: 92, y: 142},  {x: 90, y: 120},  {x: 88, y: 102},  // Pinky
    {x: 134, y: 220}, {x: 174, y: 200}                    // Palm Base
  ]);

  const videoRef = useRef<HTMLVideoElement>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const predictionInterval = useRef<number | null>(null);

  // Stop current active local camera feeds
  const stopCameraStream = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  // Launch live camera feed securely
  const startCameraStream = async () => {
    setCameraError(null);
    try {
      const constraints = { video: { width: 640, height: 480 } };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      // if (videoRef.current) {
      //   videoRef.current.srcObject = stream;
      //   videoRef.current.play().catch(e => console.warn("Video play interrupted:", e));
      // }
      setUseLiveCamera(true);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;

          videoRef.current.play().catch(e =>
            console.warn("Video play interrupted:", e)
          );
        }
      }, 100);

    } catch (err: any) {
      console.warn("Camera activation failed, fallback activated:", err);
      setCameraError(err.message || 'Permission denied or camera is in use.');
      setUseLiveCamera(false);
    }
  };

  // Sound client synthesizes beautiful success chime
  const playSuccessChime = () => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }
      
      const now = ctx.currentTime;
      
      // Dual oscillators for a rich, warm xylophone chime
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gainNode = ctx.createGain();

      osc1.type = 'sine';
      osc2.type = 'triangle';

      // Arpeggiated C major chord (C5 followed by G5)
      osc1.frequency.setValueAtTime(523.25, now); // C5
      osc1.frequency.exponentialRampToValueAtTime(1046.50, now + 0.15); // C6

      osc2.frequency.setValueAtTime(783.99, now); // G5
      osc2.frequency.exponentialRampToValueAtTime(1567.98, now + 0.15); // G6

      gainNode.gain.setValueAtTime(0.2, now);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.55);

      osc1.connect(gainNode);
      osc2.connect(gainNode);
      gainNode.connect(ctx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 0.6);
      osc2.stop(now + 0.6);
    } catch (e) {
      console.warn("Audio Context chime failed:", e);
    }
  };

  // Toggle live camera switch
  const handleCameraToggle = () => {
    if (useLiveCamera) {
      stopCameraStream();
      setUseLiveCamera(false);
    } else {
      startCameraStream();
    }
  };

  // Cleanup local webcam on component unmount
  useEffect(() => {
    return () => {
      stopCameraStream();
    };
  }, []);

  

  // Handle beginning calibration practice
  const handlePracticeStart = async () => {
    setPracticeState('calibrating');
    setProgressPercent(0);
    setFeedbackOverlay("Preparing camera...");

    if (!useLiveCamera) {
      await startCameraStream();
    }

    setTimeout(() => {
      setPracticeState('tracking');
      setFeedbackOverlay("Show gesture A.");

      predictionInterval.current = window.setInterval(
        sendFrameToBackend,
        700
      );
  },  1500);
  };

  // Return to idle state for retraining
  const handleReset = () => {
    if (predictionInterval.current !== null) {
      clearInterval(predictionInterval.current);
      predictionInterval.current = null;
    }
    setPracticeState('idle');
    setProgressPercent(0);
    setFeedbackOverlay('');

    
  };

  const sendFrameToBackend = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) return;

    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");

    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        image: imageData
      })
    });

      const data = await response.json();

      setProgressPercent(data.accuracy);
      setFeedbackOverlay(data.feedback[0]);

      if (data.status === "Correct") {
        setPracticeState("success");
      }
  };

  return (
    <div id="lessons-view" className="space-y-6">
      
      {/* Dynamic Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-extrabold tracking-widest text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              Active Module
            </span>
            <span className="text-xs font-semibold text-slate-400">
              {currentLesson.category} • {currentLesson.level}
            </span>
          </div>
          <h2 className="font-sans text-xl font-extrabold text-slate-900 mt-1">
            {currentLesson.title}
          </h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCameraToggle}
            className={`flex items-center gap-1.5 rounded-xl border px-4 py-2 font-sans text-xs font-bold transition-all cursor-pointer ${
              useLiveCamera
                ? 'bg-blue-600 border-blue-600 text-white shadow-sm'
                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            <Camera className="h-4 w-4" />
            {useLiveCamera ? 'Webcam: LIVE' : 'Webcam: Simulate'}
          </button>
        </div>
      </div>

      {/* Split-Screen Interactive Learning Section */}
      <div id="split-screen-learning" className="grid gap-6 lg:grid-cols-2">
        
        {/* Left Screen: Instructor Presentation Demonstration */}
        <div id="instructor-view-screen" className="flex flex-col rounded-2xl bg-white border border-slate-100 overflow-hidden shadow-sm">
          
          {/* Simulated HD video placeholder or real player rendering */}
          <div className="relative aspect-video w-full bg-slate-950 flex shadow-inner group">
            <img
              src={currentLesson.instructorImage}
              alt="BIM instructor presentation visual reference"
              referrerPolicy="no-referrer"
              className="h-full w-full object-cover opacity-90 transition-opacity"
            />
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent p-4 flex items-end justify-between">
              <div>
                <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest block font-mono">Expert Demonstration</span>
                <span className="font-sans text-sm font-extrabold text-white">Lesson Clip: Sign "{currentLesson.signPhrase}"</span>
              </div>
              <div className="flex items-center justify-center h-8 w-8 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white cursor-pointer hover:bg-white/20">
                <Volume2 className="h-4 w-4" />
              </div>
            </div>
            {/* Visual Ripple Focus Guide */}
            <div className="absolute top-1/4 right-1/3 h-14 w-14 rounded-full border-2 border-yellow-400/80 animate-ping pointer-events-none" title="Notice the dominant hand space"></div>
          </div>

          <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <h3 className="font-sans text-sm font-extrabold text-slate-800">Step-by-step Execution:</h3>
              <p className="font-sans text-xs text-slate-600 leading-relaxed">
                {currentLesson.description}
              </p>
            </div>

            {/* Smart tip banner */}
            <div className="rounded-lg bg-blue-50/50 p-3 flex gap-2.5 items-center border border-blue-50">
              <span className="text-base text-blue-600" title="Sign tips">💡</span>
              <p className="font-sans text-[11px] font-medium text-slate-500 leading-normal">
                <strong className="text-blue-700 font-semibold">Tip: </strong>{currentLesson.tip}
              </p>
            </div>
          </div>
        </div>

        {/* Right Screen: Interactive Camera Feed and Tracking System */}
        <div id="camera-gesture-screen" className="flex flex-col rounded-2xl bg-white border border-slate-100 overflow-hidden shadow-sm">
          
          {/* Main Camera Canvas Area */}
          <div className="relative aspect-video w-full bg-slate-900 border-b border-slate-50 overflow-hidden flex items-center justify-center">
            
            {useLiveCamera ? (
              <>
                <video
                  ref={videoRef}
                  playsInline
                  autoPlay
                  muted
                  className="h-full w-full object-cover "
                ></video>
                <canvas
                  ref={canvasRef}
                  width={640}
                  height={480}
                  className="hidden"
                ></canvas>
              </>
            ) : (
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuC29GnNTIc0h8g6dyyoP364KMi26nYgeR6MFrDjOM3kgeF3NxHWTayVg-af2db2Oq5_Iw1tXQS_vhczzuXHmO0C4en7namN3ICRxgNIkNC_3Uudd-cBNITQPPlLqKA4O_LuPmC4gZgWw_5d6qkhJPOsIH62XfrxhIbxhC9AGfF6WuovF6_QiYrY6nHyCzLqUBzCasa0tiJ0duItPL1yBss7e_WPfIlhVeOPelzy6BjTj-71pNa-UFYF3Cl-b4MmAnGc8krFSOCNEBvx"
                alt="Skeletal calibrator calibration feedback"
                referrerPolicy="no-referrer"
                className="h-full w-full object-cover opacity-80"
              />
            )}

            {/* Floating skeletal wireframe tracker lines overlay */}
            {(practiceState === 'tracking' || practiceState === 'calibrating') && (
              <svg className="absolute inset-0 h-full w-full pointer-events-none select-none z-20">
                {/* Connect Joints via wires */}
                {/* Thumb strand */}
                <line x1={skeletonJoints[0].x} y1={skeletonJoints[0].y} x2={skeletonJoints[1].x} y2={skeletonJoints[1].y} stroke="#3b82f6" strokeWidth="2.5" />
                <line x1={skeletonJoints[1].x} y1={skeletonJoints[1].y} x2={skeletonJoints[2].x} y2={skeletonJoints[2].y} stroke="#3b82f6" strokeWidth="2.5" />
                <line x1={skeletonJoints[2].x} y1={skeletonJoints[2].y} x2={skeletonJoints[3].x} y2={skeletonJoints[3].y} stroke="#3b82f6" strokeWidth="2.5" />
                
                {/* Index finger strand */}
                <line x1={skeletonJoints[16].x} y1={skeletonJoints[16].y} x2={skeletonJoints[4].x} y2={skeletonJoints[4].y} stroke="#ef4444" strokeWidth="2.5" />
                <line x1={skeletonJoints[4].x} y1={skeletonJoints[4].y} x2={skeletonJoints[5].x} y2={skeletonJoints[5].y} stroke="#ef4444" strokeWidth="2.5" />
                <line x1={skeletonJoints[5].x} y1={skeletonJoints[5].y} x2={skeletonJoints[6].x} y2={skeletonJoints[6].y} stroke="#ef4444" strokeWidth="2.5" />
                
                {/* Palm structure connections */}
                <path 
                  d={`M ${skeletonJoints[16].x} ${skeletonJoints[16].y} L ${skeletonJoints[17].x} ${skeletonJoints[17].y} Z`} 
                  stroke="#10b981" 
                  strokeWidth="3" 
                  strokeDasharray="4 2"
                />

                {/* Plot joints dots representation */}
                {skeletonJoints.map((node, i) => (
                  <circle
                    key={i}
                    cx={node.x}
                    cy={node.y}
                    r={i < 4 ? "4" : i < 7 ? "5" : "3"}
                    fill={i < 4 ? "#3b82f6" : i < 7 ? "#ef4444" : "#10b981"}
                    className="animate-pulse"
                  />
                ))}
              </svg>
            )}

            {/* Scanning Laser Line */}
            {(practiceState === 'tracking' || practiceState === 'calibrating') && (
              <div className="absolute inset-0 scanline pointer-events-none z-10"></div>
            )}

            {/* Standard Warning / Fallback Camera Alert Notification Panel */}
            {cameraError && (
              <div className="absolute top-3 left-3 right-3 bg-red-950/80 backdrop-blur-md rounded-xl p-3 border border-red-500/20 text-white flex items-start gap-2.5 z-30">
                <ShieldAlert className="h-4.5 w-4.5 shrink-0 text-red-400 mt-0.5" />
                <div className="space-y-0.5">
                  <span className="text-[11px] font-bold block leading-none text-red-200">Security / Sandboxed limit</span>
                  <span className="text-[10px] leading-tight text-slate-300 block">Using visual skeletal simulator fallback safely. All interactions are operational!</span>
                </div>
              </div>
            )}

            {/* Interactive State Feedback Badge Overlay */}
            {practiceState !== 'idle' && (
              <div className="absolute bottom-3 inset-x-3 bg-slate-950/80 backdrop-blur-md rounded-xl p-3 flex items-center justify-between text-white border border-white/10 z-30">
                <div className="space-y-1">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-blue-500 animate-ping"></span>
                    <span className="font-sans text-xs font-black uppercase tracking-wider">
                      {practiceState === 'calibrating' ? 'Calibrating Camera...' : practiceState === 'tracking' ? 'Matching Hand...' : 'Correct Gesture!'}
                    </span>
                  </div>
                  <span className="text-[9px] text-slate-300 block">{feedbackOverlay}</span>
                </div>
                {practiceState !== 'success' && (
                  <span className="font-mono text-xs font-black bg-blue-600/30 text-blue-300 px-2 py-0.5 rounded border border-blue-500/20">
                    {progressPercent}%
                  </span>
                )}
              </div>
            )}

            {/* Final Reward Perfect Form Backdrop Spark Overlay */}
            {practiceState === 'success' && (
              <div className="absolute inset-0 bg-emerald-950/90 backdrop-blur-sm z-35 flex flex-col items-center justify-center p-6 text-center animate-fade-in text-white">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500 text-3xl shadow-xl shadow-emerald-500/20 animate-bounce">
                  ✨
                </div>
                <h3 className="mt-4 font-sans text-xl font-black text-white">Perfect Form unlocked!</h3>
                <p className="mt-1.5 max-w-xs font-sans text-xs text-emerald-200 leading-normal">
                  Did you know that the letter "A" handshape can also be used in the sign for "Assalamualaikum"?"{currentLesson.signPhrase}".
                </p>
                <div className="mt-4 bg-emerald-500/20 border border-emerald-400/20 rounded-full px-3.5 py-1 text-[11px] font-bold text-emerald-300 inline-flex items-center gap-1">
                  <span className="text-yellow-400">★</span> +50 XP Experience reward
                </div>
              </div>
            )}

          </div>

          {/* Practice Controller Footer Panel */}
          <div className="p-4 flex items-center justify-between bg-slate-50/50">
            {practiceState === 'idle' ? (
              <div className="flex w-full items-center justify-between">
                <span className="text-[10px] text-slate-500 font-medium">Ready to start gesture matching?</span>
                <button
                  id="start-practice-session-btn"
                  onClick={handlePracticeStart}
                  className="flex items-center gap-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-sans text-xs font-bold px-4 py-2.5 transition-all shadow-md shadow-blue-500/10 cursor-pointer"
                >
                  <Camera className="h-4 w-4" />
                  Analyze My Form
                </button>
              </div>
            ) : practiceState === 'success' ? (
              <div className="flex w-full gap-3 justify-end">
                <button
                  id="retry-practice-btn"
                  onClick={handleReset}
                  className="rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-sans text-xs font-bold px-4 py-2.5 cursor-pointer"
                >
                  Practice Again
                </button>
                <button
                  id="next-lesson-advance-btn"
                  onClick={() => { handleReset(); nextLesson(); }}
                  className="flex items-center gap-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-sans text-xs font-bold px-4 py-2.5 shadow cursor-pointer"
                >
                  Next Lesson
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <div className="flex w-full justify-between items-center">
                <div className="h-2 w-1/3 rounded-full bg-slate-200 overflow-hidden">
                  <div className="h-full bg-blue-600 transition-all duration-100" style={{ width: `${progressPercent}%` }}></div>
                </div>
                <button
                  id="abort-calibration-btn"
                  onClick={handleReset}
                  className="text-xs text-slate-400 hover:text-slate-600 font-bold cursor-pointer"
                >
                  Abort Tracker
                </button>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
};
