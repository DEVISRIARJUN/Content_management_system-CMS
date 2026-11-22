import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, FileText, PenTool, Image, Tags, Globe, 
  Moon, Sun, Plus, Sparkles, Database, Eye, ArrowLeft,
  ChevronUp, ChevronDown, Trash2, Send, History, Check, AlertTriangle
} from 'lucide-react';
import { PostsAPI, CategoriesAPI, AnalyticsAPI, AiAPI } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Editor State
  const [editorPost, setEditorPost] = useState({
    id: null,
    title: '',
    excerpt: '',
    category_id: null,
    featured_image: '',
    blocks: [
      { id: 'b1', type: 'heading', level: 2, text: 'Introduction' },
      { id: 'b2', type: 'paragraph', text: 'Write your content with structured blocks...' }
    ],
    status: 'draft'
  });

  const [aiReadability, setAiReadability] = useState({ score: '--', grade: '', notes: '' });
  const [aiSeo, setAiSeo] = useState({ score: '--', checklist: [] });
  const [suggestedTags, setSuggestedTags] = useState([]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [dash, postList, catList] = await Promise.all([
        AnalyticsAPI.getDashboard().catch(() => null),
        PostsAPI.list().catch(() => []),
        CategoriesAPI.list().catch(() => [])
      ]);
      if (dash) setAnalytics(dash);
      if (postList) setPosts(postList.results || postList);
      if (catList) setCategories(catList.results || catList);
    } catch (e) {
      console.error(e);
    }
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark', !isDarkMode);
  };

  const runAiAnalysis = async () => {
    const content = editorPost.blocks.map(b => b.text || b.code || '').join('\n');
    try {
      const [readData, seoData, tagData] = await Promise.all([
        AiAPI.readability(content),
        AiAPI.seo({ title: editorPost.title, excerpt: editorPost.excerpt, content }),
        AiAPI.suggestTags(editorPost.title, content)
      ]);
      setAiReadability({ score: readData.flesch_score, grade: readData.grade_level, notes: readData.notes });
      setAiSeo({ score: seoData.seo_score, checklist: seoData.checklist });
      setSuggestedTags(tagData.suggested_tags || []);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className={`min-h-screen flex flex-col ${isDarkMode ? 'dark bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-slate-900 to-indigo-600 dark:from-white dark:to-indigo-400 bg-clip-text text-transparent">NovaCMS</span>
              <span className="ml-2 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">Studio</span>
            </div>
          </div>

          {/* Navigation Bar */}
          <nav className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl text-xs font-semibold">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'posts', label: 'Articles', icon: FileText },
              { id: 'editor', label: 'Builder', icon: PenTool },
              { id: 'categories', label: 'Categories', icon: Tags },
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
                    isActive ? 'bg-white dark:bg-slate-700 shadow-sm text-indigo-600 dark:text-white font-bold' : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" /> {tab.label}
                </button>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <button onClick={toggleTheme} className="w-9 h-9 rounded-lg border border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {activeTab === 'dashboard' && analytics && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-xs text-slate-500 font-semibold">Total Publications</span>
                <p className="text-2xl font-extrabold mt-1">{analytics.metrics.total_posts}</p>
                <p className="text-[11px] text-emerald-600 mt-1 font-semibold">{analytics.metrics.published_posts} Published</p>
              </div>
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-xs text-slate-500 font-semibold">Total Views</span>
                <p className="text-2xl font-extrabold mt-1">{analytics.metrics.total_views.toLocaleString()}</p>
                <p className="text-[11px] text-indigo-600 mt-1 font-semibold">Real-time telemetry</p>
              </div>
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-xs text-slate-500 font-semibold">Avg. Engagement</span>
                <p className="text-2xl font-extrabold mt-1">{analytics.metrics.avg_views_per_post}</p>
                <p className="text-[11px] text-slate-400 mt-1">Reads / Article</p>
              </div>
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
                <span className="text-xs text-slate-500 font-semibold">Engine Status</span>
                <p className="text-sm font-bold mt-2 text-indigo-600">MySQL &amp; Django DRF</p>
                <p className="text-[11px] text-slate-400 mt-1">Block JSON validated</p>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
              <h3 className="font-bold text-sm mb-3">Top Performing Articles</h3>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {analytics.top_posts.map(p => (
                  <div key={p.id} className="py-3 flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{p.title}</span>
                    <span className="font-bold text-emerald-600">{p.view_count.toLocaleString()} views</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'posts' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Articles Catalogue</h2>
              <button onClick={() => setActiveTab('editor')} className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-sm">
                <Plus className="w-4 h-4" /> New Article
              </button>
            </div>
            <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 overflow-hidden shadow-sm">
              <table className="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800 text-slate-500 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th className="p-3">Title</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Views</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {posts.map(p => (
                    <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="p-3 font-semibold">{p.title}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${p.status === 'published' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
                          {p.status}
                        </span>
                      </td>
                      <td className="p-3 font-bold text-slate-600 dark:text-slate-300">{p.view_count.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'editor' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-4">
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
                <input
                  type="text"
                  value={editorPost.title}
                  onChange={(e) => setEditorPost({ ...editorPost, title: e.target.value })}
                  placeholder="Article Title..."
                  className="w-full px-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-bold text-sm focus:outline-none"
                />
                <textarea
                  value={editorPost.excerpt}
                  onChange={(e) => setEditorPost({ ...editorPost, excerpt: e.target.value })}
                  rows={2}
                  placeholder="Short excerpt / meta description..."
                  className="w-full px-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs focus:outline-none"
                />
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                  <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500">Structured Blocks</h4>
                </div>
                {editorPost.blocks.map((block, i) => (
                  <div key={block.id} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 block mb-1">{block.type}</span>
                    <input
                      type="text"
                      value={block.text || ''}
                      onChange={(e) => {
                        const newBlocks = [...editorPost.blocks];
                        newBlocks[i].text = e.target.value;
                        setEditorPost({ ...editorPost, blocks: newBlocks });
                      }}
                      className="w-full bg-transparent text-xs font-medium focus:outline-none"
                      placeholder="Block text..."
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="lg:col-span-4 space-y-4">
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-indigo-600" /> AI Assistant</span>
                  <button onClick={runAiAnalysis} className="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 text-xs font-bold hover:bg-indigo-100">Evaluate</button>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-xs">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>Flesch Readability</span>
                    <span className="text-indigo-600 font-bold">{aiReadability.score} / 100</span>
                  </div>
                  <p className="text-[11px] text-slate-500">{aiReadability.notes || 'Click Evaluate to inspect.'}</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-xs">
                  <div className="flex justify-between font-semibold mb-1">
                    <span>SEO Health</span>
                    <span className="text-emerald-600 font-bold">{aiSeo.score} / 100</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
