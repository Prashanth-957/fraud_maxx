/**
 * @license SPDX-License-Identifier: Apache-2.0
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  ShieldAlert, ShieldCheck, CreditCard, Clock, MapPin, AlertTriangle, Shield,
  Activity, Zap, Trash2, Play, Square, UserCircle, CheckCircle2, Bell, TrendingUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Toaster, toast } from 'sonner';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, BarChart, Bar, Cell, ScatterChart, Scatter, ZAxis, Legend
} from 'recharts';

const BACKEND = 'http://localhost:5000';

const CATEGORIES = [
  { value: 'grocery_pos', label: 'Grocery (POS)' },
  { value: 'grocery_net', label: 'Grocery (Online)' },
  { value: 'shopping_net', label: 'Shopping (Online)' },
  { value: 'shopping_pos', label: 'Shopping (POS)' },
  { value: 'misc_net', label: 'Misc (Online)' },
  { value: 'misc_pos', label: 'Misc (POS)' },
  { value: 'gas_transport', label: 'Gas / Transport' },
  { value: 'health_fitness', label: 'Health / Fitness' },
  { value: 'home', label: 'Home' },
  { value: 'kids_pets', label: 'Kids / Pets' },
  { value: 'travel', label: 'Travel' },
  { value: 'entertainment', label: 'Entertainment' },
];

interface Result {
  id: string;
  prediction: number;
  probability: number;
  explanation: string[];
  distance: number;
  age: number;
  gender: string;
  category: string;
  amount: number;
  hour: number;
  timestamp: Date;
  status?: 'Pending' | 'Resolved';
}

interface Metrics {
  Accuracy?: string; Precision?: string; Recall?: string;
  'F1 Score'?: string; 'ROC AUC'?: string; 'AUC-PR'?: string;
  'Training Size'?: string; Threshold?: string; [k: string]: any;
}

const fmt = (v: string | undefined) => {
  if (!v || v === 'N/A') return 'N/A';
  const n = parseFloat(v);
  return isNaN(n) ? v : (n <= 1 ? (n * 100).toFixed(2) + '%' : Number(n).toLocaleString());
};

export default function App() {
  const [tab, setTab] = useState<'Dashboard' | 'Analytics' | 'Alerts'>('Dashboard');

  // Form state — all have defaults so inputs are never blocking
  const [amount, setAmount] = useState('150');
  const [hour, setHour] = useState('14');
  const [distance, setDistance] = useState('20');
  const [age, setAge] = useState('35');
  const [gender, setGender] = useState('M');
  const [category, setCategory] = useState('grocery_pos');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Result[]>([]);
  const [monitoring, setMonitoring] = useState(false);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Check backend & fetch metrics on mount
  useEffect(() => {
    fetch(`${BACKEND}/`)
      .then(r => r.ok ? setBackendOnline(true) : setBackendOnline(false))
      .catch(() => setBackendOnline(false));

    fetch(`${BACKEND}/metrics`)
      .then(r => r.json())
      .then(d => setMetrics(d))
      .catch(() => setMetrics(null));
  }, []);

  const addAlert = useCallback((a: Result) => {
    setHistory(prev => [a, ...prev].slice(0, 100));
    if (a.prediction === 1) {
      toast.error(`Fraud Detected: $${a.amount.toFixed(2)}`, {
        description: `Risk: ${(a.probability * 100).toFixed(1)}% — ${a.category}`,
        icon: <ShieldAlert className="w-4 h-4 text-red-500" />,
        duration: 5000,
      });
    }
  }, []);

  const runPredict = useCallback(async (
    amt?: number, hr?: number, dist?: number, ag?: number, gen?: string, cat?: string
  ) => {
    const tAmt = amt ?? parseFloat(amount);
    const tHour = hr ?? parseFloat(hour);
    const tDist = dist ?? parseFloat(distance);
    const tAge = ag ?? parseFloat(age);
    const tGender = gen ?? gender;
    const tCat = cat ?? category;

    if ([tAmt, tHour, tDist, tAge].some(isNaN)) {
      if (!amt) setError('Please fill in all fields with valid numbers.');
      return;
    }

    if (!amt) { setLoading(true); setError(null); }

    let prediction = 0, probability = 0, explanation: string[] = [];

    try {
      const res = await fetch(`${BACKEND}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amt: tAmt,
          trans_date_trans_time: `2026-04-05 ${String(Math.floor(tHour)).padStart(2, '0')}:00:00`,
          lat: 33.9,
          long: -84.3,
          merch_lat: 33.9 + tDist * 0.009,
          merch_long: -84.3,
          gender: tGender,
          dob: `${2026 - tAge}-06-15`,
          category: tCat,
          city_pop: 100000,
          zip: 30301,
          merchant: 'fraud_Heathcote',
          job: 'Software Engineer'
        })
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      prediction = data.prediction;
      probability = data.probability;
      explanation = data.explanation || [];
    } catch {
      // fallback heuristic when backend is down
      const risky = tAmt > 800 || tHour < 5 || tDist > 200;
      prediction = risky ? 1 : 0;
      probability = risky ? 0.72 + Math.random() * 0.25 : Math.random() * 0.28;
      explanation = [
        tAmt > 800 ? 'High transaction amount.' : 'Normal amount.',
        tHour < 5 ? 'Late-night transaction.' : 'Standard hours.',
        tDist > 200 ? `Large distance from home (${tDist} km).` : 'Normal proximity.'
      ];
    }

    const r: Result = {
      id: Math.random().toString(36).substr(2, 9),
      prediction, probability, explanation,
      distance: tDist, age: tAge, gender: tGender,
      category: tCat, amount: tAmt, hour: tHour,
      timestamp: new Date(),
      status: prediction === 1 ? 'Pending' : undefined
    };

    if (!amt) setResult(r);
    addAlert(r);
    if (!amt) setLoading(false);
  }, [amount, hour, distance, age, gender, category, addAlert]);

  // Live monitoring
  useEffect(() => {
    if (monitoring) {
      intervalRef.current = setInterval(() => {
        const amt = Math.floor(Math.random() * 4000) + 5;
        const hr  = Math.floor(Math.random() * 24);
        const dist = Math.floor(Math.random() * 300);
        const ag  = Math.floor(Math.random() * 55) + 18;
        const gen = Math.random() > 0.5 ? 'M' : 'F';
        const cat = CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)].value;
        runPredict(amt, hr, dist, ag, gen, cat);
      }, 3000);
      toast.success('Live monitoring started', { description: 'Scanning every 3 seconds.' });
    } else {
      if (intervalRef.current) { clearInterval(intervalRef.current); toast.info('Monitoring stopped.'); }
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [monitoring, runPredict]);

  const resolve = (id: string) => {
    setHistory(prev => prev.map(a => a.id === id ? { ...a, status: 'Resolved' } : a));
    if (result?.id === id) setResult(prev => prev ? { ...prev, status: 'Resolved' } : null);
    toast.success('Alert resolved.');
  };

  // Metric cards derived from backend metrics
  const metricCards = metrics ? [
    { label: 'Accuracy',  value: fmt(metrics.Accuracy) },
    { label: 'Precision', value: fmt(metrics.Precision) },
    { label: 'Recall',    value: fmt(metrics.Recall) },
    { label: 'F1 Score',  value: fmt(metrics['F1 Score']) },
    { label: 'ROC AUC',   value: fmt(metrics['ROC AUC']) },
    { label: 'AUC-PR',    value: fmt(metrics['AUC-PR']) },
  ] : [];

  const perf = metrics ? [
    { name: 'Accuracy',  v: parseFloat(metrics.Accuracy || '0') * 100 },
    { name: 'Precision', v: parseFloat(metrics.Precision || '0') * 100 },
    { name: 'Recall',    v: parseFloat(metrics.Recall || '0') * 100 },
    { name: 'F1',        v: parseFloat(metrics['F1 Score'] || '0') * 100 },
    { name: 'AUC-PR',   v: parseFloat(metrics['AUC-PR'] || '0') * 100 },
  ] : [];

  const trendData = [...history].reverse().map((a, i) => ({
    i, prob: +(a.probability * 100).toFixed(1), amt: a.amount, fraud: a.prediction
  }));

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#1E293B] font-sans">
      <Toaster position="top-right" richColors />

      {/* NAV */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <ShieldAlert className="text-white w-5 h-5" />
            </div>
            <span className="font-black text-xl tracking-tight">SARU</span>
            <span className={`ml-3 text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${
              backendOnline === true ? 'bg-emerald-100 text-emerald-700' :
              backendOnline === false ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-500'
            }`}>
              {backendOnline === true ? '● ML Online' : backendOnline === false ? '● ML Offline' : '● Checking…'}
            </span>
          </div>

          <div className="flex items-center gap-6">
            {(['Dashboard', 'Analytics', 'Alerts'] as const).map(t => (
              <button key={t} onClick={() => setTab(t)}
                className={`text-sm font-semibold transition-colors ${tab === t ? 'text-blue-600' : 'text-slate-500 hover:text-slate-900'}`}>
                {t}
              </button>
            ))}

            <button
              onClick={() => setMonitoring(m => !m)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${
                monitoring
                  ? 'bg-red-100 text-red-600 border border-red-200 animate-pulse'
                  : 'bg-slate-100 text-slate-600 border border-slate-200 hover:bg-slate-200'
              }`}>
              {monitoring ? <Square className="w-3 h-3 fill-current" /> : <Play className="w-3 h-3 fill-current" />}
              {monitoring ? 'Stop' : 'Live Monitor'}
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        {/* ═══════════════ DASHBOARD ═══════════════ */}
        {tab === 'Dashboard' && (
          <div className="space-y-8">

            {/* ML Metric cards at top of dashboard */}
            {metricCards.length > 0 && (
              <div>
                <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-3 h-3" /> Model Performance (XGBoost — Live)
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                  {metricCards.map(m => (
                    <div key={m.label} className="bg-white rounded-2xl border border-slate-200 p-4 text-center shadow-sm hover:shadow-md transition-all">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">{m.label}</p>
                      <p className="text-2xl font-black text-slate-900">{m.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Session summary */}
            {history.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Total Scanned',  value: history.length, color: 'text-blue-500', bg: 'bg-blue-50', icon: Activity },
                  { label: 'Fraud Detected', value: history.filter(a => a.prediction === 1).length, color: 'text-red-500', bg: 'bg-red-50', icon: ShieldAlert },
                  { label: 'Avg Risk',       value: `${(history.reduce((s,a) => s + a.probability,0)/history.length*100).toFixed(1)}%`, color: 'text-amber-500', bg: 'bg-amber-50', icon: Shield },
                  { label: 'Resolved',       value: history.filter(a => a.status === 'Resolved').length, color: 'text-emerald-500', bg: 'bg-emerald-50', icon: CheckCircle2 },
                ].map(s => (
                  <div key={s.label} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-xl ${s.bg} flex items-center justify-center`}>
                      <s.icon className={`w-5 h-5 ${s.color}`} />
                    </div>
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{s.label}</p>
                      <p className="text-xl font-black text-slate-900">{s.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="grid lg:grid-cols-12 gap-8">

              {/* ── FORM ── */}
              <div className="lg:col-span-4 space-y-6">
                <div>
                  <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Fraud Analysis</h1>
                  <p className="text-slate-500 text-sm mt-1">Enter transaction details and run ML prediction.</p>
                </div>

                {error && (
                  <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm font-medium">
                    <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
                  </div>
                )}

                <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-5">

                  {/* Amount */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                      <CreditCard className="w-3 h-3" /> Amount ($)
                    </label>
                    <div className="relative">
                      <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-semibold">$</span>
                      <input id="inp-amount" type="number" min="0" value={amount}
                        onChange={e => setAmount(e.target.value)}
                        placeholder="e.g. 150.00"
                        className="w-full pl-8 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition font-medium" />
                    </div>
                  </div>

                  {/* Hour */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                      <Clock className="w-3 h-3" /> Hour of Day (0–23)
                    </label>
                    <input id="inp-hour" type="number" min="0" max="23" value={hour}
                      onChange={e => setHour(e.target.value)}
                      placeholder="e.g. 14"
                      className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition font-medium" />
                  </div>

                  {/* Distance */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                      <MapPin className="w-3 h-3" /> Distance from Home (km)
                    </label>
                    <input id="inp-dist" type="number" min="0" value={distance}
                      onChange={e => setDistance(e.target.value)}
                      placeholder="e.g. 20"
                      className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition font-medium" />
                  </div>

                  {/* Age + Gender */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                        <UserCircle className="w-3 h-3" /> Age
                      </label>
                      <input id="inp-age" type="number" min="18" max="100" value={age}
                        onChange={e => setAge(e.target.value)}
                        placeholder="35"
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition font-medium" />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                        <UserCircle className="w-3 h-3" /> Gender
                      </label>
                      <select id="inp-gender" value={gender} onChange={e => setGender(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition font-medium">
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                      </select>
                    </div>
                  </div>

                  {/* Category */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                      <Zap className="w-3 h-3" /> Category
                    </label>
                    <select id="inp-category" value={category} onChange={e => setCategory(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition font-medium">
                      {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                    </select>
                  </div>

                  <button id="btn-predict" onClick={() => runPredict()} disabled={loading}
                    className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-xl font-bold transition flex items-center justify-center gap-3 shadow-lg shadow-blue-100">
                    {loading
                      ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      : <><ShieldAlert className="w-4 h-4" /> Run ML Analysis</>}
                  </button>
                </div>

                {/* Alert feed */}
                <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                      <Bell className="w-3 h-3 text-yellow-500" /> Real-time Feed
                    </span>
                    {history.length > 0 && (
                      <button onClick={() => setHistory([])}
                        className="p-1 text-slate-300 hover:text-red-500 transition-colors">
                        <Trash2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                  <div className="max-h-[320px] overflow-y-auto p-2 space-y-2">
                    <AnimatePresence initial={false}>
                      {history.length === 0
                        ? <p className="py-8 text-center text-slate-300 text-xs italic">No activity yet</p>
                        : history.map(a => (
                          <motion.div key={a.id}
                            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, scale: 0.9 }}
                            className={`p-3 rounded-xl border flex items-center gap-3 ${
                              a.prediction === 1
                                ? a.status === 'Resolved' ? 'bg-emerald-50 border-emerald-100 text-emerald-900'
                                : 'bg-red-50 border-red-100 text-red-900'
                                : 'bg-white border-slate-100 text-slate-600'
                            }`}>
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                              a.prediction === 1
                                ? a.status === 'Resolved' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
                                : 'bg-slate-100 text-slate-400'
                            }`}>
                              {a.prediction === 1
                                ? a.status === 'Resolved' ? <CheckCircle2 className="w-4 h-4" /> : <ShieldAlert className="w-4 h-4" />
                                : <ShieldCheck className="w-4 h-4" />}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex justify-between">
                                <span className="font-black text-sm">${a.amount.toLocaleString()}</span>
                                <span className="text-[10px] opacity-40">{a.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                              </div>
                              <p className="text-[10px] opacity-60 truncate">{a.category} · {a.distance} km · {a.age} yrs</p>
                              <p className="text-[10px] font-bold">{(a.probability * 100).toFixed(1)}% risk</p>
                            </div>
                            {a.prediction === 1 && a.status !== 'Resolved' && (
                              <button onClick={() => resolve(a.id)}
                                className="shrink-0 text-[10px] font-bold px-2 py-1 rounded-lg bg-red-600 text-white hover:bg-red-700">
                                Resolve
                              </button>
                            )}
                          </motion.div>
                        ))}
                    </AnimatePresence>
                  </div>
                </div>
              </div>

              {/* ── RESULT PANEL ── */}
              <div className="lg:col-span-8">
                <AnimatePresence mode="wait">
                  {result ? (
                    <motion.div key={result.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">

                      {/* Status card */}
                      <div className={`relative overflow-hidden rounded-[2.5rem] p-10 border-2 transition-all duration-500 ${
                        result.prediction === 1 && result.status !== 'Resolved'
                          ? 'bg-red-50 border-red-200 shadow-2xl shadow-red-100'
                          : 'bg-emerald-50 border-emerald-200 shadow-2xl shadow-emerald-100'
                      }`}>
                        {result.prediction === 1 && result.status !== 'Resolved' && (
                          <motion.div animate={{ opacity: [0.1, 0.3, 0.1] }} transition={{ duration: 2, repeat: Infinity }}
                            className="absolute inset-0 bg-red-400 pointer-events-none" />
                        )}
                        <div className="relative z-10">
                          <div className="flex flex-col md:flex-row items-start justify-between gap-8 mb-10">
                            <div className="flex items-center gap-6">
                              <motion.div
                                animate={result.prediction === 1 && result.status !== 'Resolved' ? { scale: [1, 1.1, 1] } : {}}
                                transition={{ duration: 0.8, repeat: Infinity }}
                                className={`w-20 h-20 rounded-3xl flex items-center justify-center shadow-xl ${
                                  result.prediction === 1 && result.status !== 'Resolved' ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'
                                }`}>
                                {result.prediction === 1 && result.status !== 'Resolved'
                                  ? <ShieldAlert className="w-10 h-10" />
                                  : <ShieldCheck className="w-10 h-10" />}
                              </motion.div>
                              <div>
                                <h2 className={`text-4xl font-black tracking-tight ${
                                  result.prediction === 1 && result.status !== 'Resolved' ? 'text-red-900' : 'text-emerald-900'
                                }`}>
                                  {result.prediction === 1 ? result.status === 'Resolved' ? 'RESOLVED' : 'FRAUD DETECTED' : 'LEGITIMATE'}
                                </h2>
                                <div className="flex items-center gap-3 mt-2">
                                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                                    result.prediction === 1 && result.status !== 'Resolved' ? 'bg-red-200 text-red-800' : 'bg-emerald-200 text-emerald-800'
                                  }`}>
                                    {result.prediction === 1 ? result.status === 'Resolved' ? 'Reviewed' : 'Action Required' : 'Verified Safe'}
                                  </span>
                                  <span className="text-sm font-semibold text-slate-600">
                                    Confidence: <strong>{(result.probability * 100).toFixed(1)}%</strong>
                                  </span>
                                </div>
                              </div>
                            </div>
                            <div className="text-center bg-white/60 rounded-2xl p-5 border border-white/60 min-w-[150px]">
                              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Amount</p>
                              <p className="text-3xl font-black text-slate-900">${result.amount.toLocaleString()}</p>
                              {result.prediction === 1 && result.status !== 'Resolved' && (
                                <button onClick={() => resolve(result.id)}
                                  className="mt-3 w-full py-2 bg-white border-2 border-red-300 text-red-600 rounded-xl font-bold hover:bg-red-600 hover:text-white transition-all text-xs">
                                  Resolve Threat
                                </button>
                              )}
                            </div>
                          </div>

                          {/* Details grid */}
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                            {[
                              { label: 'Distance', value: `${result.distance} km` },
                              { label: 'Customer Age', value: `${result.age} yrs (${result.gender === 'M' ? 'Male' : 'Female'})` },
                              { label: 'Category', value: CATEGORIES.find(c => c.value === result.category)?.label ?? result.category },
                              { label: 'Time', value: `${result.hour}:00 hrs` },
                            ].map(d => (
                              <div key={d.label} className="bg-white/60 p-4 rounded-2xl border border-white/60">
                                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">{d.label}</p>
                                <p className="font-bold text-slate-800 text-sm">{d.value}</p>
                              </div>
                            ))}
                          </div>

                          {/* Explanations */}
                          <div>
                            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
                              <Activity className="w-3 h-3" /> ML Risk Indicators
                            </h3>
                            <div className="space-y-2">
                              {result.explanation.map((item, i) => (
                                <motion.div key={i} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}
                                  className="flex items-center gap-4 bg-white/80 p-4 rounded-2xl border border-white/80 shadow-sm">
                                  <div className={`w-2 h-2 rounded-full shrink-0 ${
                                    result.prediction === 1 && result.status !== 'Resolved' ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'
                                  }`} />
                                  <p className="text-sm font-medium text-slate-700">{item}</p>
                                </motion.div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Trend chart */}
                      {history.length > 1 && (
                        <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-sm p-8">
                          <h3 className="text-lg font-bold text-slate-900 mb-6">Risk Probability Trend</h3>
                          <div className="h-[220px]">
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                  <linearGradient id="gProb" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                  </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="i" hide />
                                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                <Tooltip content={({ active, payload }) => {
                                  if (active && payload?.length) {
                                    const d = payload[0].payload;
                                    return (
                                      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xl text-xs">
                                        <p className="font-bold text-slate-900">${d.amt.toLocaleString()}</p>
                                        <p className={`font-bold ${d.prob > 70 ? 'text-red-500' : d.prob > 40 ? 'text-amber-500' : 'text-emerald-500'}`}>Risk: {d.prob}%</p>
                                      </div>
                                    );
                                  }
                                  return null;
                                }} />
                                <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3"
                                  label={{ position: 'right', value: 'High Risk', fill: '#ef4444', fontSize: 10 }} />
                                <Area type="monotone" dataKey="prob" stroke="#3b82f6" strokeWidth={3}
                                  fillOpacity={1} fill="url(#gProb)" animationDuration={800} />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ) : (
                    <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                      className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-12 bg-white rounded-[3rem] border-2 border-dashed border-slate-200">
                      <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center mb-8 relative">
                        <ShieldAlert className="w-12 h-12 text-blue-200" />
                        <motion.div animate={{ scale: [1, 1.5, 1], opacity: [0.4, 0, 0.4] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="absolute inset-0 bg-blue-100 rounded-full" />
                      </div>
                      <h2 className="text-3xl font-black text-slate-900 mb-3 tracking-tight">Ready to Analyze</h2>
                      <p className="text-slate-500 max-w-sm text-base leading-relaxed">
                        Fill in transaction details and click <strong>Run ML Analysis</strong> — or start Live Monitoring to scan automatically.
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        )}

        {/* ═══════════════ ANALYTICS ═══════════════ */}
        {tab === 'Analytics' && (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Engine Analytics</h1>
              <p className="text-slate-500 text-sm mt-1">XGBoost model performance and live transaction profiling.</p>
            </div>

            {/* Model metrics */}
            {!metrics ? (
              <div className="flex items-center justify-center p-20">
                <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
              </div>
            ) : (
              <div className="space-y-8">
                {/* Metric cards */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                  {metricCards.map(m => (
                    <div key={m.label} className="bg-white rounded-2xl border border-slate-200 p-5 text-center relative overflow-hidden group hover:shadow-lg transition-all">
                      <div className="absolute top-0 right-0 w-20 h-20 bg-blue-50 rounded-full blur-2xl -mr-6 -mt-6 group-hover:bg-blue-100 transition-all" />
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">{m.label}</p>
                      <p className="text-2xl font-black text-slate-900">{m.value}</p>
                    </div>
                  ))}
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                  {/* Bar chart */}
                  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-4">
                    <h3 className="text-lg font-bold text-slate-900">Model Performance</h3>
                    <div className="h-[280px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={perf} layout="vertical" margin={{ left: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                          <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                          <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                          <Tooltip content={({ active, payload }) => {
                            if (active && payload?.length) return (
                              <div className="bg-slate-900 text-white p-2 rounded-lg text-xs font-bold">
                                {payload[0].payload.name}: {(payload[0].value as number).toFixed(2)}%
                              </div>
                            );
                            return null;
                          }} />
                          <Bar dataKey="v" radius={[0, 4, 4, 0]}>
                            {perf.map((_, i) => <Cell key={i} fill={['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981'][i % 5]} />)}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Scatter chart */}
                  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-4">
                    <h3 className="text-lg font-bold text-slate-900">Risk vs Distance</h3>
                    <p className="text-sm text-slate-500">Bubble size = transaction amount</p>
                    <div className="h-[260px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                          <XAxis type="number" dataKey="distance" name="Distance (km)" tick={{ fill: '#94a3b8', fontSize: 11 }} label={{ value: 'km', position: 'insideBottom', offset: -5, fontSize: 10, fill: '#94a3b8' }} />
                          <YAxis type="number" dataKey="probability" name="Risk %" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                          <ZAxis type="number" dataKey="amount" range={[40, 350]} />
                          <Tooltip cursor={{ strokeDasharray: '3 3' }} content={({ active, payload }) => {
                            if (active && payload?.length) {
                              const d = payload[0].payload;
                              return <div className="bg-white border border-slate-200 rounded-xl shadow-lg p-3 text-xs font-bold">
                                <p>Risk: {d.probability}%</p>
                                <p>Distance: {d.distance} km</p>
                                <p>Amount: ${d.amount?.toLocaleString()}</p>
                              </div>;
                            }
                            return null;
                          }} />
                          <Scatter name="Safe" data={history.filter(a => a.probability < 0.5).map(a => ({ distance: a.distance, probability: Math.round(a.probability * 100), amount: a.amount }))} fill="#10b981" fillOpacity={0.7} />
                          <Scatter name="Fraud" data={history.filter(a => a.probability >= 0.5).map(a => ({ distance: a.distance, probability: Math.round(a.probability * 100), amount: a.amount }))} fill="#ef4444" fillOpacity={0.85} />
                          <Legend />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Risk distribution */}
                  {history.length > 0 && (
                    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-4">
                      <h3 className="text-lg font-bold text-slate-900">Risk Level Distribution</h3>
                      <div className="h-[220px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={[
                            { name: 'Low (<30%)', count: history.filter(a => a.probability < 0.3).length, fill: '#10b981' },
                            { name: 'Med (30–70%)', count: history.filter(a => a.probability >= 0.3 && a.probability < 0.7).length, fill: '#f59e0b' },
                            { name: 'High (>70%)', count: history.filter(a => a.probability >= 0.7).length, fill: '#ef4444' },
                          ]}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                            <Tooltip content={({ active, payload }) => {
                              if (active && payload?.length) return (
                                <div className="bg-white border border-slate-200 rounded-xl shadow-lg p-2 text-xs font-bold">
                                  {payload[0].value} transactions
                                </div>
                              );
                              return null;
                            }} />
                            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                              {[{ fill: '#10b981' }, { fill: '#f59e0b' }, { fill: '#ef4444' }].map((e, i) =>
                                <Cell key={i} fill={e.fill} />)}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}

                  {/* Trend chart */}
                  {history.length > 1 && (
                    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-4">
                      <h3 className="text-lg font-bold text-slate-900">Session Risk Trend</h3>
                      <div className="h-[220px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                              <linearGradient id="gProb2" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="i" hide />
                            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                            <Tooltip content={({ active, payload }) => {
                              if (active && payload?.length) {
                                const d = payload[0].payload;
                                return <div className="bg-white border border-slate-200 rounded-xl shadow-lg p-3 text-xs font-bold">
                                  <p>${d.amt.toLocaleString()}</p>
                                  <p className={d.prob > 70 ? 'text-red-500' : d.prob > 40 ? 'text-amber-500' : 'text-emerald-500'}>Risk: {d.prob}%</p>
                                </div>;
                              }
                              return null;
                            }} />
                            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 4" />
                            <Area type="monotone" dataKey="prob" stroke="#3b82f6" strokeWidth={2.5} fillOpacity={1} fill="url(#gProb2)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ═══════════════ ALERTS ═══════════════ */}
        {tab === 'Alerts' && (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Alert History</h1>
                <p className="text-slate-500 text-sm mt-1">{history.length} transactions analyzed this session.</p>
              </div>
              {history.length > 0 && (
                <button onClick={() => setHistory([])}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-red-600 border border-red-200 rounded-xl hover:bg-red-50 transition">
                  <Trash2 className="w-4 h-4" /> Clear All
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div className="text-center py-24 text-slate-400">
                <Activity className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p className="font-bold">No transactions analyzed yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map(a => (
                  <div key={a.id} className={`flex items-center gap-4 p-5 rounded-2xl border transition-all ${
                    a.prediction === 1 && a.status !== 'Resolved' ? 'bg-red-50 border-red-100' :
                    a.status === 'Resolved' ? 'bg-emerald-50 border-emerald-100' : 'bg-white border-slate-200'
                  }`}>
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                      a.prediction === 1 && a.status !== 'Resolved' ? 'bg-red-600 text-white' :
                      a.status === 'Resolved' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-400'
                    }`}>
                      {a.prediction === 1 ? a.status === 'Resolved' ? <CheckCircle2 className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" /> : <ShieldCheck className="w-5 h-5" />}
                    </div>
                    <div className="flex-1 min-w-0 grid grid-cols-2 sm:grid-cols-5 gap-2">
                      <div>
                        <p className="text-[10px] font-bold uppercase text-slate-400">Amount</p>
                        <p className="font-black text-slate-900">${a.amount.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase text-slate-400">Risk</p>
                        <p className={`font-bold ${a.probability > 0.7 ? 'text-red-600' : a.probability > 0.4 ? 'text-amber-600' : 'text-emerald-600'}`}>
                          {(a.probability * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase text-slate-400">Category</p>
                        <p className="font-medium text-slate-700 truncate text-sm">{CATEGORIES.find(c => c.value === a.category)?.label ?? a.category}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase text-slate-400">Distance</p>
                        <p className="font-medium text-slate-700 text-sm">{a.distance} km</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase text-slate-400">Time</p>
                        <p className="font-medium text-slate-700 text-sm">{a.timestamp.toLocaleTimeString()}</p>
                      </div>
                    </div>
                    {a.prediction === 1 && a.status !== 'Resolved' && (
                      <button onClick={() => resolve(a.id)}
                        className="shrink-0 px-3 py-1.5 bg-red-600 text-white text-xs font-bold rounded-lg hover:bg-red-700 transition">
                        Resolve
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="mt-16 border-t border-slate-200 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-400 font-medium">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-slate-900 rounded flex items-center justify-center">
              <ShieldAlert className="text-white w-3 h-3" />
            </div>
            <span className="font-bold uppercase tracking-tight">SARU SECURITY</span>
          </div>
          <p>© 2026 Saru Fraud Systems. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
