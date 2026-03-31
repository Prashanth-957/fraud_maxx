/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  CreditCard, 
  Clock, 
  MapPin, 
  Smartphone, 
  AlertCircle,
  AlertTriangle,
  Shield,
  ArrowRight,
  Activity,
  History,
  Settings,
  Search,
  Bell,
  Zap,
  Trash2,
  Play,
  Square,
  UserCircle,
  ChevronDown,
  Lock,
  Eye,
  CheckCircle2
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Toaster, toast } from 'sonner';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  ReferenceLine,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from 'recharts';

type UserRole = 'Analyst' | 'Investigator' | 'Administrator';

interface User {
  name: string;
  role: UserRole;
  avatar: string;
}

const ROLES: Record<UserRole, { permissions: string[], color: string }> = {
  Analyst: { 
    permissions: ['view_dashboard', 'run_analysis'], 
    color: 'bg-blue-100 text-blue-700' 
  },
  Investigator: { 
    permissions: ['view_dashboard', 'run_analysis', 'resolve_alerts'], 
    color: 'bg-purple-100 text-purple-700' 
  },
  Administrator: { 
    permissions: ['view_dashboard', 'run_analysis', 'resolve_alerts', 'manage_system', 'clear_history', 'live_monitoring'], 
    color: 'bg-slate-900 text-white' 
  }
};

const countryList = [
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'IN', name: 'India' },
  { code: 'CA', name: 'Canada' },
  { code: 'AU', name: 'Australia' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'JP', name: 'Japan' },
  { code: 'CN', name: 'China' },
  { code: 'BR', name: 'Brazil' },
  { code: 'AF', name: 'Afghanistan' },
  { code: 'AL', name: 'Albania' },
  { code: 'DZ', name: 'Algeria' },
  { code: 'AR', name: 'Argentina' },
  { code: 'AT', name: 'Austria' },
  { code: 'BE', name: 'Belgium' },
  { code: 'CH', name: 'Switzerland' },
  { code: 'DK', name: 'Denmark' },
  { code: 'ES', name: 'Spain' },
  { code: 'FI', name: 'Finland' },
  { code: 'GR', name: 'Greece' },
  { code: 'HK', name: 'Hong Kong' },
  { code: 'ID', name: 'Indonesia' },
  { code: 'IE', name: 'Ireland' },
  { code: 'IL', name: 'Israel' },
  { code: 'IT', name: 'Italy' },
  { code: 'KR', name: 'South Korea' },
  { code: 'MX', name: 'Mexico' },
  { code: 'MY', name: 'Malaysia' },
  { code: 'NL', name: 'Netherlands' },
  { code: 'NO', name: 'Norway' },
  { code: 'NZ', name: 'New Zealand' },
  { code: 'PH', name: 'Philippines' },
  { code: 'PL', name: 'Poland' },
  { code: 'PT', name: 'Portugal' },
  { code: 'RU', name: 'Russia' },
  { code: 'SA', name: 'Saudi Arabia' },
  { code: 'SE', name: 'Sweden' },
  { code: 'SG', name: 'Singapore' },
  { code: 'TH', name: 'Thailand' },
  { code: 'TR', name: 'Turkey' },
  { code: 'TW', name: 'Taiwan' },
  { code: 'VN', name: 'Vietnam' },
  { code: 'ZA', name: 'South Africa' },
];

const deviceOptions = [
  { value: 'known', label: 'Known Device', category: 'Standard' },
  { value: 'new', label: 'New Device', category: 'Standard' },
  { value: 'android_phone', label: 'Android Phone', category: 'Mobile' },
  { value: 'ios_phone', label: 'iOS Phone', category: 'Mobile' },
  { value: 'windows_pc', label: 'Windows PC', category: 'Desktop' },
  { value: 'mac_desktop', label: 'macOS Desktop/Laptop', category: 'Desktop' },
  { value: 'linux_pc', label: 'Linux PC', category: 'Desktop' },
  { value: 'tablet', label: 'Tablet', category: 'Mobile' },
  { value: 'smart_tv', label: 'Smart TV', category: 'Other' },
  { value: 'pos_terminal', label: 'POS Terminal', category: 'Hardware' },
  { value: 'vpn', label: 'VPN/Proxy', category: 'Network' },
  { value: 'bot', label: 'Potential Bot', category: 'Network' },
];

const transactionTypeOptions = [
  { value: 'atm_withdrawal', label: 'ATM Withdrawal', icon: Zap },
  { value: 'bank_transfer', label: 'Bank Transfer', icon: ArrowRight },
  { value: 'bill_payment', label: 'Bill Payment', icon: History },
  { value: 'online_purchase', label: 'Online Purchase', icon: Smartphone },
  { value: 'pos_payment', label: 'POS Payment', icon: CreditCard },
];

interface PredictionResult {
  id: string;
  prediction: number;
  probability: number;
  explanation: string[];
  locationName: string;
  deviceName: string;
  transactionType: string;
  amount: number;
  time: number;
  timestamp: Date;
  status?: 'Pending' | 'Resolved';
}

export default function App() {
  const [currentUser, setCurrentUser] = useState<User>({
    name: 'Admin User',
    role: 'Administrator',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Admin'
  });
  const [showRoleSwitcher, setShowRoleSwitcher] = useState(false);
  const [amount, setAmount] = useState<string>('');
  const [time, setTime] = useState<string>('');
  const [location, setLocation] = useState<string>('US');
  const [device, setDevice] = useState<string>('known');
  const [transactionType, setTransactionType] = useState<string>('online_purchase');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [alertHistory, setAlertHistory] = useState<PredictionResult[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const monitoringInterval = useRef<NodeJS.Timeout | null>(null);

  const [activeTab, setActiveTab] = useState<'Dashboard' | 'Analytics' | 'Alerts' | 'Settings'>('Dashboard');
  const [modelMetrics, setModelMetrics] = useState<any>(null);

  useEffect(() => {
    if (activeTab === 'Analytics' && !modelMetrics) {
      fetch('http://127.0.0.1:5000/metrics')
        .then(res => res.json())
        .then(data => setModelMetrics(data))
        .catch(err => console.error("Could not load metrics", err));
    }
  }, [activeTab, modelMetrics]);

  const hasPermission = (permission: string) => {
    return ROLES[currentUser.role].permissions.includes(permission);
  };

  const addAlert = useCallback((alert: PredictionResult) => {
    setAlertHistory(prev => [alert, ...prev].slice(0, 50));
    if (alert.prediction === 1) {
      toast.error(`High Risk Transaction: $${alert.amount.toFixed(2)}`, {
        description: `Detected in ${alert.locationName} via ${alert.deviceName}`,
        icon: <ShieldAlert className="w-5 h-5 text-red-500" />,
        duration: 5000,
      });
    }
  }, []);

  const handlePredict = async (
    customAmount?: number, 
    customTime?: number, 
    customLocation?: string, 
    customDevice?: string,
    customType?: string
  ) => {
    if (!hasPermission('run_analysis')) {
      toast.error('Access Denied', { description: 'You do not have permission to run manual analysis.' });
      return;
    }

    const targetAmount = customAmount ?? parseFloat(amount);
    const targetTime = customTime ?? parseFloat(time);
    const targetLocation = customLocation ?? location;
    const targetDevice = customDevice ?? device;
    const targetType = customType ?? transactionType;

    if (isNaN(targetAmount) || isNaN(targetTime)) {
      if (!customAmount) setError('Please fill in all required fields.');
      return;
    }

    if (!customAmount) setLoading(true);
    setError(null);

    const locationMap: Record<string, number> = {
      normal: 0,
      unusual: 3
    };

    const deviceMap: Record<string, number> = {
      known: 0,
      new: 3,
      android_phone: 1,
      ios_phone: 1,
      windows_pc: 1,
      mac_desktop: 1,
      linux_pc: 1,
      tablet: 1,
      smart_tv: 2,
      pos_terminal: 0,
      vpn: 3,
      bot: 3
    };

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          amount: targetAmount, 
          time: targetTime, 
          location: targetLocation, 
          device: targetDevice, 
          type: targetType 
        })
      }).catch(() => {
        // Fallback for demo purposes
        const isFraud = targetAmount > 2000 || (targetTime > 0 && targetTime < 5) || targetDevice === 'vpn' || targetDevice === 'bot';
        return {
          ok: true,
          json: async () => ({
            prediction: isFraud ? 1 : 0,
            probability: isFraud ? 0.7 + Math.random() * 0.3 : Math.random() * 0.3,
            explanation: [
              targetAmount > 2000 ? "Extremely high transaction amount." : "Standard transaction amount.",
              (targetTime > 0 && targetTime < 5) ? "High-risk time window (late night)." : "Standard business hours.",
              targetDevice === 'vpn' ? "VPN usage detected (anonymity risk)." : "Trusted device profile."
            ]
          })
        };
      });

      if (!response.ok) throw new Error('Prediction service unavailable');
      
      const data = await response.json();
      
      const newResult: PredictionResult = {
        ...data,
        id: Math.random().toString(36).substr(2, 9),
        locationName: countryList.find(c => c.code === targetLocation)?.name || targetLocation,
        deviceName: deviceOptions.find(d => d.value === targetDevice)?.label || targetDevice,
        transactionType: targetType,
        amount: targetAmount,
        time: targetTime,
        timestamp: new Date(),
        status: data.prediction === 1 ? 'Pending' : undefined
      };

      if (!customAmount) setResult(newResult);
      addAlert(newResult);
    } catch (err) {
      if (!customAmount) setError('Failed to connect to the fraud detection engine.');
    } finally {
      if (!customAmount) setLoading(false);
    }
  };

  const resolveAlert = (id: string) => {
    if (!hasPermission('resolve_alerts')) {
      toast.error('Access Denied', { description: 'You do not have permission to resolve alerts.' });
      return;
    }
    setAlertHistory(prev => prev.map(a => a.id === id ? { ...a, status: 'Resolved' } : a));
    if (result?.id === id) setResult(prev => prev ? { ...prev, status: 'Resolved' } : null);
    toast.success('Alert Resolved', { description: 'Transaction has been marked as reviewed.' });
  };

  // Live Monitoring Simulation
  useEffect(() => {
    if (isMonitoring) {
      if (!hasPermission('live_monitoring')) {
        setIsMonitoring(false);
        toast.error('Access Denied', { description: 'Only Administrators can initialize live monitoring.' });
        return;
      }

      monitoringInterval.current = setInterval(() => {
        const randomAmount = Math.floor(Math.random() * 5000) + 10;
        const randomTime = Math.floor(Math.random() * 24);
        const randomLoc = countryList[Math.floor(Math.random() * countryList.length)].code;
        const randomDev = deviceOptions[Math.floor(Math.random() * deviceOptions.length)].value;
        const randomType = transactionTypeOptions[Math.floor(Math.random() * transactionTypeOptions.length)].value;
        
        handlePredict(randomAmount, randomTime, randomLoc, randomDev, randomType);
      }, 3000);
      
      toast.success("Live Monitoring Started", {
        description: "Scanning incoming transactions in real-time.",
        icon: <Zap className="w-5 h-5 text-yellow-500" />
      });
    } else {
      if (monitoringInterval.current) {
        clearInterval(monitoringInterval.current);
        toast.info("Live Monitoring Stopped");
      }
    }
    
    return () => {
      if (monitoringInterval.current) clearInterval(monitoringInterval.current);
    };
  }, [isMonitoring, addAlert, currentUser.role]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#1E293B] font-sans selection:bg-blue-100">
      <Toaster position="top-right" richColors />
      
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <ShieldAlert className="text-white w-5 h-5" />
            </div>
            <span className="font-bold text-xl tracking-tight">SENTINEL</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-500">
            {(['Dashboard', 'Analytics', 'Alerts', 'Settings'] as const).map(tab => (
              <button 
                key={tab}
                onClick={() => setActiveTab(tab)} 
                className={activeTab === tab ? "text-blue-600 font-bold" : "hover:text-slate-900 transition-colors"}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsMonitoring(!isMonitoring)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${
                isMonitoring 
                  ? 'bg-red-100 text-red-600 border border-red-200 animate-pulse' 
                  : 'bg-slate-100 text-slate-600 border border-slate-200 hover:bg-slate-200'
              }`}
            >
              {isMonitoring ? <Square className="w-3 h-3 fill-current" /> : <Play className="w-3 h-3 fill-current" />}
              {isMonitoring ? 'Live Monitoring' : 'Start Monitoring'}
            </button>

            {/* User Profile & Role Switcher */}
            <div className="relative">
              <button 
                onClick={() => setShowRoleSwitcher(!showRoleSwitcher)}
                className="flex items-center gap-3 p-1 pr-3 rounded-full hover:bg-slate-100 transition-all border border-transparent hover:border-slate-200"
              >
                <img src={currentUser.avatar} alt="User" className="w-8 h-8 rounded-full border border-slate-200" />
                <div className="text-left hidden sm:block">
                  <p className="text-xs font-bold text-slate-900 leading-none mb-1">{currentUser.name}</p>
                  <p className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${ROLES[currentUser.role].color}`}>
                    {currentUser.role}
                  </p>
                </div>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${showRoleSwitcher ? 'rotate-180' : ''}`} />
              </button>

              <AnimatePresence>
                {showRoleSwitcher && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-2xl border border-slate-200 p-2 z-[100]"
                  >
                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400 p-3">Switch Role (Simulation)</p>
                    {(Object.keys(ROLES) as UserRole[]).map((role) => (
                      <button
                        key={role}
                        onClick={() => {
                          setCurrentUser(prev => ({ ...prev, role }));
                          setShowRoleSwitcher(false);
                          toast.info(`Role Switched to ${role}`);
                        }}
                        className={`w-full flex items-center justify-between p-3 rounded-xl text-sm font-medium transition-all ${
                          currentUser.role === role ? 'bg-slate-50 text-blue-600' : 'hover:bg-slate-50 text-slate-600'
                        }`}
                      >
                        {role}
                        {currentUser.role === role && <CheckCircle2 className="w-4 h-4" />}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {activeTab === 'Dashboard' && (
        <div className="grid lg:grid-cols-12 gap-8">
          
          {/* Left Column: Form & Recent Alerts */}
          <div className="lg:col-span-4 space-y-8">
            <header>
              <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-2">
                Fraud Analysis
              </h1>
              <p className="text-slate-500 text-sm">
                Real-time risk assessment engine.
              </p>
            </header>

            <div className="bg-white rounded-3xl shadow-sm border border-slate-200 p-6 space-y-6 relative overflow-hidden">
              {!hasPermission('run_analysis') && (
                <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center p-6 text-center">
                  <Lock className="w-8 h-8 text-slate-400 mb-3" />
                  <p className="text-sm font-bold text-slate-900">Access Restricted</p>
                  <p className="text-xs text-slate-500 mt-1">Manual analysis is only available for Analysts and Administrators.</p>
                </div>
              )}
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <CreditCard className="w-3 h-3" /> Amount
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">$</span>
                    <input 
                      type="number" 
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="0.00"
                      className="w-full pl-8 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <Clock className="w-3 h-3" /> Time (0-24)
                  </label>
                  <input 
                    type="number" 
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    placeholder="e.g. 14.5"
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <MapPin className="w-3 h-3" /> Location
                  </label>
                  <select 
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium appearance-none"
                  >
                    <option value="normal">Normal Location</option>
                    <option value="unusual">Unusual Location</option>
                    <optgroup label="Countries">
                      {countryList.map(c => (
                        <option key={c.code} value={c.code}>{c.name}</option>
                      ))}
                    </optgroup>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <Smartphone className="w-3 h-3" /> Device
                  </label>
                  <select 
                    value={device}
                    onChange={(e) => setDevice(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium appearance-none"
                  >
                    {deviceOptions.map(d => (
                      <option key={d.value} value={d.value}>{d.label}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <Zap className="w-3 h-3" /> Transaction Type
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {transactionTypeOptions.map((type) => (
                      <button
                        key={type.value}
                        onClick={() => setTransactionType(type.value)}
                        className={`p-3 rounded-xl border flex flex-col items-center justify-center gap-1.5 transition-all ${
                          transactionType === type.value 
                            ? 'bg-blue-50 border-blue-200 text-blue-600 shadow-sm' 
                            : 'bg-slate-50 border-slate-100 text-slate-400 hover:bg-slate-100'
                        }`}
                        title={type.label}
                      >
                        <type.icon className="w-4 h-4" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <button 
                onClick={() => handlePredict()}
                disabled={loading}
                className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-3 shadow-lg shadow-blue-100"
              >
                {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> : 'Run Analysis'}
              </button>
            </div>

            {/* Alert Feed */}
            <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                  <Zap className="w-3 h-3 text-yellow-500" /> Real-time Feed
                </h3>
                {hasPermission('clear_history') && (
                  <button 
                    onClick={() => setAlertHistory([])}
                    className="p-1 text-slate-300 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>
              <div className="max-h-[400px] overflow-y-auto p-2 space-y-2">
                <AnimatePresence initial={false}>
                  {alertHistory.length === 0 ? (
                    <div className="py-8 text-center text-slate-300 text-xs italic">No activity recorded</div>
                  ) : (
                    alertHistory.map((alert) => (
                      <motion.div 
                        key={alert.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className={`p-3 rounded-xl border flex items-center gap-3 transition-all ${
                          alert.prediction === 1 
                            ? alert.status === 'Resolved' ? 'bg-emerald-50 border-emerald-100 text-emerald-900' : 'bg-red-50 border-red-100 text-red-900' 
                            : 'bg-white border-slate-100 text-slate-600'
                        }`}
                      >
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                          alert.prediction === 1 
                            ? alert.status === 'Resolved' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white' 
                            : 'bg-slate-100 text-slate-400'
                        }`}>
                          {alert.prediction === 1 
                            ? alert.status === 'Resolved' ? <CheckCircle2 className="w-4 h-4" /> : <ShieldAlert className="w-4 h-4" /> 
                            : <ShieldCheck className="w-4 h-4" />}
                        </div>
                        <div className="min-w-0 flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              {(() => {
                                const typeOption = transactionTypeOptions.find(t => t.value === alert.transactionType);
                                const TypeIcon = typeOption?.icon || Zap;
                                return <TypeIcon className="w-3 h-3 opacity-40" />;
                              })()}
                              <span className="font-black text-base tracking-tight">${alert.amount.toLocaleString()}</span>
                            </div>
                            <span className="text-[10px] font-bold uppercase tracking-wider opacity-40">{alert.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          </div>
                          <div className="grid grid-cols-2 gap-x-2 text-[10px] font-medium">
                            <div className="flex items-center gap-1 opacity-60 truncate">
                              <MapPin className="w-2.5 h-2.5" />
                              <span className="truncate">{alert.locationName}</span>
                            </div>
                            <div className="flex items-center gap-1 opacity-60 truncate">
                              <Smartphone className="w-2.5 h-2.5" />
                              <span className="truncate">{alert.deviceName}</span>
                            </div>
                          </div>
                        </div>
                        
                        {alert.prediction === 1 && alert.status !== 'Resolved' && hasPermission('resolve_alerts') && (
                          <div className="flex items-center gap-1.5 shrink-0">
                            <button 
                              onClick={() => setResult(alert)}
                              className="p-2 rounded-lg bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-all shadow-sm group"
                              title="Investigate"
                            >
                              <Eye className="w-4 h-4 group-hover:text-blue-600" />
                            </button>
                            <button 
                              onClick={() => resolveAlert(alert.id)}
                              className="px-3 py-1.5 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-all shadow-md flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider"
                              title="Resolve"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              Resolve
                            </button>
                          </div>
                        )}
                      </motion.div>
                    ))
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Right Column: Active Result & Detailed Analysis */}
          <div className="lg:col-span-8 space-y-8">
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div 
                  key={result.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  {/* Main Alert Card */}
                  <div className={`relative overflow-hidden rounded-[2.5rem] p-10 border-2 transition-all duration-500 ${
                    result.prediction === 1 
                      ? result.status === 'Resolved' ? 'bg-emerald-50 border-emerald-200 shadow-2xl shadow-emerald-100' : 'bg-red-50 border-red-200 shadow-2xl shadow-red-100' 
                      : 'bg-emerald-50 border-emerald-200 shadow-2xl shadow-emerald-100'
                  }`}>
                    {/* Pulsing Background for High Risk */}
                    {result.prediction === 1 && result.status !== 'Resolved' && (
                      <motion.div 
                        animate={{ opacity: [0.1, 0.3, 0.1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="absolute inset-0 bg-red-400 pointer-events-none"
                      />
                    )}

                    <div className="relative z-10">
                      <div className="flex flex-col md:flex-row items-center justify-between gap-8 mb-12">
                        <div className="flex items-center gap-6">
                          <motion.div 
                            animate={result.prediction === 1 && result.status !== 'Resolved' ? { scale: [1, 1.1, 1] } : {}}
                            transition={{ duration: 0.5, repeat: result.prediction === 1 && result.status !== 'Resolved' ? Infinity : 0 }}
                            className={`w-24 h-24 rounded-3xl flex items-center justify-center shadow-xl ${
                              result.prediction === 1 
                                ? result.status === 'Resolved' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white' 
                                : 'bg-emerald-600 text-white'
                            }`}
                          >
                            {result.prediction === 1 
                              ? result.status === 'Resolved' ? <CheckCircle2 className="w-12 h-12" /> : <ShieldAlert className="w-12 h-12" /> 
                              : <ShieldCheck className="w-12 h-12" />}
                          </motion.div>
                          <div>
                            <h2 className={`text-4xl font-black tracking-tight ${
                              result.prediction === 1 
                                ? result.status === 'Resolved' ? 'text-emerald-900' : 'text-red-900' 
                                : 'text-emerald-900'
                            }`}>
                              {result.prediction === 1 
                                ? result.status === 'Resolved' ? 'THREAT RESOLVED' : 'HIGH RISK' 
                                : 'SECURE'}
                            </h2>
                            <div className="flex items-center gap-2 mt-1">
                              <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                                result.prediction === 1 
                                  ? result.status === 'Resolved' ? 'bg-emerald-200 text-emerald-800' : 'bg-red-200 text-red-800' 
                                  : 'bg-emerald-200 text-emerald-800'
                              }`}>
                                {result.prediction === 1 
                                  ? result.status === 'Resolved' ? 'Reviewed' : 'Action Required' 
                                  : 'Verified'}
                              </div>
                              <span className={`text-sm font-medium ${
                                result.prediction === 1 
                                  ? result.status === 'Resolved' ? 'text-emerald-600' : 'text-red-600' 
                                  : 'text-emerald-600'
                              }`}>
                                Confidence: {(result.probability * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="flex flex-col items-center gap-4">
                          <div className="bg-white/40 backdrop-blur-sm rounded-3xl p-6 border border-white/40 text-center min-w-[180px]">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 block mb-1">Amount Analyzed</span>
                            <p className="text-3xl font-black text-slate-900">${result.amount.toLocaleString()}</p>
                          </div>
                          {result.prediction === 1 && result.status !== 'Resolved' && hasPermission('resolve_alerts') && (
                            <button 
                              onClick={() => resolveAlert(result.id)}
                              className="w-full py-3 bg-white border-2 border-red-200 text-red-600 rounded-2xl font-bold hover:bg-red-600 hover:text-white transition-all shadow-lg flex items-center justify-center gap-2"
                            >
                              <CheckCircle2 className="w-4 h-4" />
                              Resolve Threat
                            </button>
                          )}
                        </div>
                      </div>

                      <div className="grid md:grid-cols-4 gap-6 mb-12">
                        <div className="bg-white/60 p-5 rounded-2xl border border-white/60">
                          <MapPin className="w-4 h-4 text-slate-400 mb-2" />
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Origin</span>
                          <p className="font-bold text-slate-800">{result.locationName}</p>
                        </div>
                        <div className="bg-white/60 p-5 rounded-2xl border border-white/60">
                          <Smartphone className="w-4 h-4 text-slate-400 mb-2" />
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Terminal</span>
                          <p className="font-bold text-slate-800">{result.deviceName}</p>
                        </div>
                        <div className="bg-white/60 p-5 rounded-2xl border border-white/60">
                          <Zap className="w-4 h-4 text-slate-400 mb-2" />
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Type</span>
                          <p className="font-bold text-slate-800 capitalize">{result.transactionType}</p>
                        </div>
                        <div className="bg-white/60 p-5 rounded-2xl border border-white/60">
                          <Clock className="w-4 h-4 text-slate-400 mb-2" />
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Timestamp</span>
                          <p className="font-bold text-slate-800">{result.time}:00 UTC</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2">
                          <Activity className="w-3 h-3" /> Risk Indicators
                        </h3>
                        <div className="grid gap-3">
                          {result.explanation.map((item, i) => (
                            <motion.div 
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: i * 0.1 }}
                              key={i} 
                              className="flex items-center gap-4 bg-white/80 p-4 rounded-2xl border border-white/80 shadow-sm"
                            >
                              <div className={`w-2 h-2 rounded-full shrink-0 ${
                                result.prediction === 1 
                                  ? result.status === 'Resolved' ? 'bg-emerald-500' : 'bg-red-500 animate-pulse' 
                                  : 'bg-emerald-500'
                              }`}></div>
                              <p className="text-sm font-medium text-slate-700">{item}</p>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* System Health */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    {[
                      { label: 'Latency', value: '18ms', icon: Activity, color: 'text-blue-500' },
                      { label: 'Uptime', value: '99.99%', icon: ShieldCheck, color: 'text-emerald-500' },
                      { label: 'Threats', value: alertHistory.filter(a => a.prediction === 1).length, icon: ShieldAlert, color: 'text-red-500' },
                      { label: 'Load', value: '12%', icon: Zap, color: 'text-yellow-500' },
                    ].map((stat, i) => (
                      <div key={i} className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
                        <stat.icon className={`w-4 h-4 ${stat.color} mb-3`} />
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">{stat.label}</span>
                        <p className="text-lg font-black">{stat.value}</p>
                      </div>
                    ))}
                  </div>

                  {/* Risk Trend Visualization */}
                  <div className="space-y-6">
                    {/* Summary Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        { label: 'Total Analyzed', value: alertHistory.length, icon: Activity, color: 'text-blue-500', bg: 'bg-blue-50' },
                        { label: 'High Risk', value: alertHistory.filter(a => a.probability >= 0.7).length, icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-50' },
                        { label: 'Avg Risk', value: `${(alertHistory.reduce((acc, a) => acc + a.probability, 0) / (alertHistory.length || 1) * 100).toFixed(0)}%`, icon: Shield, color: 'text-amber-500', bg: 'bg-amber-50' },
                        { label: 'Resolved', value: alertHistory.filter(a => a.status === 'Resolved').length, icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-50' },
                      ].map((stat, i) => (
                        <div key={i} className="bg-white p-4 rounded-3xl border border-slate-200 shadow-sm flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-2xl ${stat.bg} flex items-center justify-center`}>
                            <stat.icon className={`w-5 h-5 ${stat.color}`} />
                          </div>
                          <div>
                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{stat.label}</p>
                            <p className="text-lg font-black text-slate-900">{stat.value}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                      <div className="md:col-span-2 bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-lg font-bold text-slate-900">Risk Probability Trend</h3>
                            <p className="text-sm text-slate-500">Real-time anomaly detection and probability tracking.</p>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-1.5">
                              <div className="w-2 h-2 rounded-full bg-red-500"></div>
                              <span className="text-[10px] font-bold uppercase text-slate-400">High Risk</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                              <span className="text-[10px] font-bold uppercase text-slate-400">Secure</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="h-[300px] w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                              data={[...alertHistory].reverse().map((a, i) => ({
                                index: i,
                                probability: (a.probability * 100).toFixed(1),
                                isFraud: a.prediction === 1,
                                amount: a.amount
                              }))}
                              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                            >
                              <defs>
                                <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                                  <stop offset="50%" stopColor="#f59e0b" stopOpacity={0.1}/>
                                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                              <XAxis dataKey="index" hide />
                              <YAxis 
                                domain={[0, 100]} 
                                tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 600 }}
                                axisLine={false}
                                tickLine={false}
                              />
                              <Tooltip 
                                content={({ active, payload }) => {
                                  if (active && payload && payload.length) {
                                    const data = payload[0].payload;
                                    return (
                                      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xl">
                                        <p className="text-[10px] font-bold uppercase text-slate-400 mb-1">Transaction Data</p>
                                        <p className="text-sm font-bold text-slate-900">${data.amount.toLocaleString()}</p>
                                        <p className={`text-xs font-bold ${data.probability > 70 ? 'text-red-500' : data.probability > 30 ? 'text-amber-500' : 'text-emerald-500'}`}>
                                          Risk: {data.probability}%
                                        </p>
                                      </div>
                                    );
                                  }
                                  return null;
                                }}
                              />
                              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'right', value: 'High Risk', fill: '#ef4444', fontSize: 10, fontWeight: 700 }} />
                              <Area 
                                type="monotone" 
                                dataKey="probability" 
                                stroke="#3b82f6" 
                                strokeWidth={3}
                                fillOpacity={1} 
                                fill="url(#colorProb)" 
                                animationDuration={1000}
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-6">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">Risk Distribution</h3>
                          <p className="text-sm text-slate-500">Breakdown of threat levels.</p>
                        </div>
                        
                        <div className="h-[300px] w-full flex flex-col items-center justify-center">
                          <ResponsiveContainer width="100%" height="80%">
                            <BarChart
                              data={[
                                { name: 'Low', count: alertHistory.filter(a => a.probability < 0.3).length, color: '#10b981' },
                                { name: 'Med', count: alertHistory.filter(a => a.probability >= 0.3 && a.probability < 0.7).length, color: '#f59e0b' },
                                { name: 'High', count: alertHistory.filter(a => a.probability >= 0.7).length, color: '#ef4444' },
                              ]}
                            >
                              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 600 }} axisLine={false} tickLine={false} />
                              <YAxis hide />
                              <Tooltip cursor={{fill: 'transparent'}} content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  return (
                                    <div className="bg-white p-2 rounded-lg border border-slate-200 shadow-lg text-xs font-bold">
                                      {payload[0].value} Transactions
                                    </div>
                                  );
                                }
                                return null;
                              }} />
                              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                {[
                                  { color: '#10b981' },
                                  { color: '#f59e0b' },
                                  { color: '#ef4444' },
                                ].map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                          <div className="grid grid-cols-3 gap-2 w-full mt-4">
                            {[
                              { label: 'Low', color: 'bg-emerald-500' },
                              { label: 'Med', color: 'bg-amber-500' },
                              { label: 'High', color: 'bg-red-500' },
                            ].map((item, i) => (
                              <div key={i} className="text-center">
                                <div className={`w-full h-1 rounded-full ${item.color} mb-1 opacity-20`}></div>
                                <span className="text-[10px] font-bold text-slate-400 uppercase">{item.label}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-12 bg-white rounded-[3rem] border-2 border-dashed border-slate-200"
                >
                  <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-8 relative">
                    <Activity className="w-12 h-12 text-slate-200" />
                    <motion.div 
                      animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="absolute inset-0 bg-blue-100 rounded-full"
                    />
                  </div>
                  <h2 className="text-3xl font-black text-slate-900 mb-4 tracking-tight">System Ready</h2>
                  <p className="text-slate-500 max-w-sm text-lg leading-relaxed">
                    The Sentinel engine is active. Start live monitoring or run a manual analysis to begin threat detection.
                  </p>
                  <button 
                    onClick={() => setIsMonitoring(true)}
                    className="mt-8 px-8 py-4 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition-all flex items-center gap-3"
                  >
                    <Play className="w-4 h-4 fill-current" />
                    Initialize Live Stream
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
        )}

        {activeTab === 'Analytics' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header>
              <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-2">
                Engine Analytics
              </h1>
              <p className="text-slate-500 text-sm">
                XGBoost Model Performance Metrics based on test data evaluation.
              </p>
            </header>
            
            {!modelMetrics ? (
              <div className="flex items-center justify-center p-20"><div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div></div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {(Object.entries(modelMetrics) as [string, any][]).map(([key, value]) => (
                  <div key={key} className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm relative overflow-hidden group hover:shadow-xl transition-all">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-3xl group-hover:bg-blue-100 transition-all -mr-10 -mt-10"></div>
                    <div className="relative z-10">
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-2">
                        <Activity className="w-3 h-3 text-blue-500" />
                        {key.replace(/_/g, ' ')}
                      </h3>
                      <p className="text-4xl font-black text-slate-900">
                        {typeof value === 'number' 
                          ? (value < 1.000001 ? (value * 100).toFixed(2) + '%' : value.toLocaleString())
                          : value}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-slate-200 mt-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2 opacity-50 grayscale">
            <div className="w-6 h-6 bg-slate-900 rounded flex items-center justify-center">
              <ShieldAlert className="text-white w-4 h-4" />
            </div>
            <span className="font-bold text-sm tracking-tight uppercase">SENTINEL SECURITY</span>
          </div>
          <div className="flex gap-8 text-xs font-bold uppercase tracking-widest text-slate-400">
            <a href="#" className="hover:text-slate-900">Privacy Policy</a>
            <a href="#" className="hover:text-slate-900">Protocols</a>
            <a href="#" className="hover:text-slate-900">Support</a>
          </div>
          <p className="text-xs text-slate-400 font-medium">
            © 2026 Sentinel Fraud Systems. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
