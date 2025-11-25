import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, Clock, Database } from 'lucide-react';

function Dashboard() {
  const [status, setStatus] = useState({ status: 'loading', jobs: [] });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/status');
        const data = await res.json();
        setStatus(data);
      } catch (err) {
        setStatus({ status: 'error', jobs: [] });
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <Activity className="text-blue-500" />
          Automation Dashboard
        </h2>
        <div className={`px-4 py-2 rounded-full flex items-center gap-2 ${
          status.status === 'connected' ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
        }`}>
          <Database className="w-4 h-4" />
          {status.status === 'connected' ? 'Firebase Connected' : 'Offline'}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Total Processed</h3>
          <p className="text-3xl font-bold">0</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Pending</h3>
          <p className="text-3xl font-bold text-yellow-500">0</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Completed</h3>
          <p className="text-3xl font-bold text-green-500">0</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Failed</h3>
          <p className="text-3xl font-bold text-red-500">0</p>
        </div>
      </div>

      {/* Jobs Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h3 className="text-xl font-semibold">Recent Pipeline Jobs</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Repository</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Time</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {/* Placeholder Row */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-white">Waiting for data...</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-700 text-gray-300">
                    Idle
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  -
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  -
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
