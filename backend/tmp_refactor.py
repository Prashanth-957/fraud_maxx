import sys

with open(r'c:\Users\prashanth\Downloads\fraud\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace arrays
text = text.split("const countryList = [")[0] + """
const transactionCategoryOptions = [
  { value: 'grocery_pos', label: 'Grocery (POS)' },
  { value: 'grocery_net', label: 'Grocery (Online)' },
  { value: 'shopping_net', label: 'Shopping (Online)' },
  { value: 'shopping_pos', label: 'Shopping (POS)' },
  { value: 'misc_net', label: 'Misc (Online)' },
  { value: 'misc_pos', label: 'Misc (POS)' },
  { value: 'gas_transport', label: 'Gas/Transport' },
  { value: 'health_fitness', label: 'Health/Fitness' },
  { value: 'home', label: 'Home' },
  { value: 'kids_pets', label: 'Kids/Pets' },
  { value: 'travel', label: 'Travel' },
  { value: 'entertainment', label: 'Entertainment' },
];

const genderOptions = [
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' }
];

interface PredictionResult {
  id: string;
  prediction: number;
  probability: number;
  explanation: string[];
  distance: number;
  age: number;
  gender: string;
  category: string;
  amount: number;
  time: number;
  timestamp: Date;
  status?: 'Pending' | 'Resolved';
}
""" + text.split("export default function App() {")[1]

text = text.replace("App() {", "export default function App() {\n")

# 2. State replacements
text = text.replace(
"""  const [location, setLocation] = useState<string>('US');
  const [device, setDevice] = useState<string>('known');
  const [transactionType, setTransactionType] = useState<string>('online_purchase');""", 
"""  const [distance, setDistance] = useState<string>('20');
  const [age, setAge] = useState<string>('30');
  const [category, setCategory] = useState<string>('grocery_pos');
  const [gender, setGender] = useState<string>('M');"""
)

# 3. HandlePredict signature
old_hp = """  const handlePredict = async (
    customAmount?: number, 
    customTime?: number, 
    customLocation?: string, 
    customDevice?: string,
    customType?: string
  ) => {"""

new_hp = """  const handlePredict = async (
    customAmount?: number, 
    customTime?: number, 
    customDistance?: number, 
    customAge?: number,
    customCategory?: string,
    customGender?: string
  ) => {"""

text = text.replace(old_hp, new_hp)

# 4. HandlePredict parsing
old_hp_body1 = """    const targetAmount = customAmount ?? parseFloat(amount);
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
    };"""

new_hp_body1 = """    const targetAmount = customAmount ?? parseFloat(amount);
    const targetTime = customTime ?? parseFloat(time);
    const targetDistance = customDistance ?? parseFloat(distance);
    const targetAge = customAge ?? parseFloat(age);
    const targetCategory = customCategory ?? category;
    const targetGender = customGender ?? gender;

    if (isNaN(targetAmount) || isNaN(targetTime) || isNaN(targetDistance) || isNaN(targetAge)) {
      if (!customAmount) setError('Please fill in all required fields.');
      return;
    }

    if (!customAmount) setLoading(true);
    setError(null);"""

text = text.replace(old_hp_body1, new_hp_body1)

# 5. HandlePredict Fetch
old_fetch = """      const response = await fetch("https://fraud-detection-q454.onrender.com/predict", {
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
      });"""

new_fetch = """      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          amt: targetAmount, 
          trans_date_trans_time: `2026-04-05 ${targetTime.toString().padStart(2, '0')}:00:00`, 
          lat: 0, 
          long: 0, 
          merch_lat: 0,
          merch_long: targetDistance / 111.0,
          gender: targetGender,
          dob: `${2026 - targetAge}-01-01`,
          category: targetCategory,
          city_pop: 100000,
          zip: 10000,
          merchant: "fraud_Kihn",
          job: "Software Engineer"
        })
      }).catch(() => {
        // Fallback for demo purposes
        const isFraud = targetAmount > 2000 || (targetTime > 0 && targetTime < 5) || targetDistance > 500;
        return {
          ok: true,
          json: async () => ({
            prediction: isFraud ? 1 : 0,
            probability: isFraud ? 0.7 + Math.random() * 0.3 : Math.random() * 0.3,
            explanation: [
              targetAmount > 2000 ? "Extremely high transaction amount." : "Standard transaction amount.",
              (targetTime > 0 && targetTime < 5) ? "High-risk time window (late night)." : "Standard business hours.",
              targetDistance > 500 ? "Unusually large distance from user typical location." : "Standard location proximity."
            ]
          })
        };
      });"""
text = text.replace(old_fetch, new_fetch)

# 6. Response parsing in HandlePredict
old_res = """      const newResult: PredictionResult = {
        ...data,
        id: Math.random().toString(36).substr(2, 9),
        locationName: countryList.find(c => c.code === targetLocation)?.name || targetLocation,
        deviceName: deviceOptions.find(d => d.value === targetDevice)?.label || targetDevice,
        transactionType: targetType,
        amount: targetAmount,
        time: targetTime,
        timestamp: new Date(),
        status: data.prediction === 1 ? 'Pending' : undefined
      };"""

new_res = """      const newResult: PredictionResult = {
        ...data,
        id: Math.random().toString(36).substr(2, 9),
        distance: targetDistance,
        age: targetAge,
        gender: targetGender,
        category: targetCategory,
        amount: targetAmount,
        time: targetTime,
        timestamp: new Date(),
        status: data.prediction === 1 ? 'Pending' : undefined
      };"""
text = text.replace(old_res, new_res)

# 7. Form UI
old_form_ui = """                <div className="space-y-2">
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
                </div>"""

new_form_ui = """                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <MapPin className="w-3 h-3" /> Distance from Home (km)
                  </label>
                  <input 
                    type="number"
                    value={distance}
                    onChange={(e) => setDistance(e.target.value)}
                    placeholder="e.g. 15"
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium appearance-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                        <UserCircle className="w-3 h-3" /> Age
                      </label>
                      <input 
                        type="number"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        placeholder="e.g. 35"
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium appearance-none"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                        <UserCircle className="w-3 h-3" /> Gender
                      </label>
                      <select 
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium appearance-none"
                      >
                        {genderOptions.map(d => (
                          <option key={d.value} value={d.value}>{d.label}</option>
                        ))}
                      </select>
                    </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <Zap className="w-3 h-3" /> Category
                  </label>
                  <select 
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium appearance-none"
                  >
                    {transactionCategoryOptions.map(d => (
                      <option key={d.value} value={d.value}>{d.label}</option>
                    ))}
                  </select>
                </div>"""
text = text.replace(old_form_ui, new_form_ui)

# 8. Alert display UI
text = text.replace("alert.transactionType", "alert.category")
text = text.replace("alert.locationName", "alert.distance + ' km'")
text = text.replace("alert.deviceName", "alert.age + ' yrs (' + alert.gender + ')'")

text = text.replace("result.locationName", "result.distance + ' km'")
text = text.replace("result.deviceName", "result.age + ' yrs'")
text = text.replace("result.transactionType", "result.category")

# Live Monitoring
old_live = """      monitoringInterval.current = setInterval(() => {
        const randomAmount = Math.floor(Math.random() * 5000) + 10;
        const randomTime = Math.floor(Math.random() * 24);
        const randomLoc = countryList[Math.floor(Math.random() * countryList.length)].code;
        const randomDev = deviceOptions[Math.floor(Math.random() * deviceOptions.length)].value;
        const randomType = transactionTypeOptions[Math.floor(Math.random() * transactionTypeOptions.length)].value;
        
        handlePredict(randomAmount, randomTime, randomLoc, randomDev, randomType);
      }, 3000);"""

new_live = """      monitoringInterval.current = setInterval(() => {
        const randomAmount = Math.floor(Math.random() * 5000) + 10;
        const randomTime = Math.floor(Math.random() * 24);
        const randomDist = Math.floor(Math.random() * 100);
        const randomAge = Math.floor(Math.random() * 60) + 18;
        const randomCat = transactionCategoryOptions[Math.floor(Math.random() * transactionCategoryOptions.length)].value;
        const randomGender = Math.random() > 0.5 ? 'M' : 'F';
        
        handlePredict(randomAmount, randomTime, randomDist, randomAge, randomCat, randomGender);
      }, 3000);"""
text = text.replace(old_live, new_live)

text = text.replace("fetch('https://fraud-detection-q454.onrender.com/metrics')", "fetch('http://localhost:5000/metrics')")

with open(r'c:\Users\prashanth\Downloads\fraud\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done refs")
