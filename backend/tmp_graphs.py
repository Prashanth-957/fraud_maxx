import sys

with open(r'c:\Users\prashanth\Downloads\fraud\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace recharts imports
old_recharts = """  PieChart,
  Pie
} from 'recharts';"""

new_recharts = """  PieChart,
  Pie,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  ZAxis,
  Legend
} from 'recharts';"""
text = text.replace(old_recharts, new_recharts)

# Change Analytics Tab Rendering
old_analytics = """        {activeTab === 'Analytics' && (
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
        )}"""

new_analytics = """        {activeTab === 'Analytics' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header>
              <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-2">
                Engine Analytics
              </h1>
              <p className="text-slate-500 text-sm">
                In-depth breakdown of ML model execution and transaction profiling.
              </p>
            </header>
            
            {!modelMetrics ? (
              <div className="flex items-center justify-center p-20"><div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div></div>
            ) : (
              <div className="space-y-8">
                {/* Metrics Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC', 'AUC-PR'].filter(k => modelMetrics[k]).map((key) => (
                    <div key={key} className="bg-white p-6 rounded-[2rem] border border-slate-200 shadow-sm relative overflow-hidden group hover:shadow-xl transition-all">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full blur-3xl group-hover:bg-blue-100 transition-all -mr-10 -mt-10"></div>
                        <div className="relative z-10">
                        <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1 flex items-center gap-2">
                            <Activity className="w-3 h-3 text-blue-500" />
                            {key}
                        </h3>
                        <p className="text-3xl font-black text-slate-900">
                            {modelMetrics[key]}
                        </p>
                        </div>
                    </div>
                    ))}
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {/* Model Performance Comparison Bar Chart */}
                    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-6">
                        <h3 className="text-lg font-bold text-slate-900">Core Performance Metrics</h3>
                        <div className="h-[300px] w-full">
                          <ResponsiveContainer width="100%" height="100%">
                              <BarChart
                                  data={[
                                      { name: 'Accuracy', value: parseFloat(modelMetrics['Accuracy'] || '0') },
                                      { name: 'Precision', value: parseFloat(modelMetrics['Precision'] || '0') },
                                      { name: 'Recall', value: parseFloat(modelMetrics['Recall'] || '0') },
                                      { name: 'F1 Score', value: parseFloat(modelMetrics['F1 Score'] || '0') },
                                      { name: 'AUC-PR', value: parseFloat(modelMetrics['AUC-PR'] || '0') }
                                  ]}
                                  layout="vertical"
                                  margin={{ left: 20 }}
                              >
                                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                                  <XAxis type="number" domain={[0, 100]} hide />
                                  <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 700, fill: '#64748b' }} />
                                  <Tooltip cursor={{fill: '#f8fafc'}} content={({ active, payload }) => {
                                      if (active && payload && payload.length) {
                                          return (
                                              <div className="bg-slate-900 text-white p-3 rounded-xl shadow-xl text-xs font-bold">
                                                  {payload[0].payload.name}: {payload[0].value}%
                                              </div>
                                          )
                                      }
                                      return null;
                                  }} />
                                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                      {
                                          [0,1,2,3,4].map((i) => <Cell key={i} fill={['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'][i%5]} />)
                                      }
                                  </Bar>
                              </BarChart>
                          </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Threat Distance vs Prediction Scatter */}
                    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm space-y-6">
                        <h3 className="text-lg font-bold text-slate-900">Risk by Transaction Distance</h3>
                        <div className="h-[300px] w-full">
                          <ResponsiveContainer width="100%" height="100%">
                              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                  <XAxis type="number" dataKey="distance" name="Distance (km)" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                                  <YAxis type="number" dataKey="probability" name="Risk %" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                                  <ZAxis type="number" dataKey="amount" range={[50, 400]} />
                                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                                  <Scatter name="Low Risk" data={alertHistory.filter(a => a.probability < 0.5).map(a => ({ distance: a.distance, probability: Math.round(a.probability*100), amount: a.amount, category: a.category }))} fill="#10b981" fillOpacity={0.6} />
                                  <Scatter name="High Risk" data={alertHistory.filter(a => a.probability >= 0.5).map(a => ({ distance: a.distance, probability: Math.round(a.probability*100), amount: a.amount, category: a.category }))} fill="#ef4444" fillOpacity={0.8} />
                                  <Legend />
                              </ScatterChart>
                          </ResponsiveContainer>
                        </div>
                    </div>
                </div>

              </div>
            )}
          </div>
        )}"""

text = text.replace(old_analytics, new_analytics)
with open(r'c:\Users\prashanth\Downloads\fraud\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated analytics graphs!")
