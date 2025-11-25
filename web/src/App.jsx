import React, { useState, useEffect } from 'react';
import VoiceRecorder from './components/VoiceRecorder';
import Dashboard from './components/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    // Placeholder for fetching blog posts
    setPosts([
      {
        id: 1,
        title: "Example Repo - Solving Developer Pain Points",
        date: "2025-11-23",
        repo: "example/awesome-project",
        status: "Published"
      }
    ]);
  }, []);

  const tabs = [
    { id: 'dashboard', name: '📊 Dashboard', icon: '📊' },
    { id: 'recorder', name: '🎙️ Voice Studio', icon: '🎙️' },
    { id: 'posts', name: '📝 Blog Posts', icon: '📝' },
    { id: 'videos', name: '🎬 Videos', icon: '🎬' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Open Source Video Generator
            </h1>
            <div className="flex gap-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 font-medium ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span className="hidden md:inline">{tab.name.split(' ')[1]}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="animate-in fade-in duration-500">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'recorder' && <VoiceRecorder />}

        {activeTab === 'posts' && (
          <div className="max-w-4xl mx-auto p-8">
            <h2 className="text-3xl font-bold mb-6">Blog Posts</h2>
            <div className="grid gap-6">
              {posts.map(post => (
                <div key={post.id} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition-colors">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-2xl font-semibold mb-2">{post.title}</h3>
                      <p className="text-gray-400 text-sm">Repo: {post.repo}</p>
                    </div>
                    <span className="px-3 py-1 bg-green-900 text-green-300 rounded-full text-sm font-medium">
                      {post.status}
                    </span>
                  </div>
                  <div className="flex gap-4 mt-6">
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">
                      View Post
                    </button>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors">
                      Watch Video
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'videos' && (
          <div className="max-w-6xl mx-auto p-8">
            <h2 className="text-3xl font-bold mb-6">Generated Videos</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div className="aspect-video bg-gray-900 rounded-lg mb-4 flex items-center justify-center">
                  <span className="text-gray-500">Video Preview</span>
                </div>
                <h3 className="font-semibold mb-2">Example Project - EN</h3>
                <p className="text-sm text-gray-400">English • 20s</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
