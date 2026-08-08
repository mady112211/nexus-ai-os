'use client';

import { useRouter, usePathname } from 'next/navigation';
import { removeToken } from '@/lib/api';
import NotificationBell from './NotificationBell';
import ThemeToggle from './ThemeToggle';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '🏠' },
  { label: 'Command Center', path: '/chat', icon: '💬' },
  { label: 'Workspaces', path: '/workspaces', icon: '🏢' },
  { label: 'Missions', path: '/missions', icon: '🎯' },
  { label: 'Agents', path: '/agents', icon: '🤖' },
  { label: 'Plugins', path: '/plugins', icon: '🔌' },
  { label: 'Tools', path: '/tools', icon: '🛠️' },
  { label: 'Memory', path: '/memory', icon: '🧠' },
  { label: 'Analytics', path: '/analytics', icon: '📊' },
  { label: 'Self-Mod', path: '/self-mod', icon: '🧬' },
  { label: 'Settings', path: '/settings', icon: '⚙️' },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    removeToken();
    router.push('/');
  };

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 min-h-screen flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-sm text-white">
              N
            </div>
            <div>
              <div className="font-bold text-sm text-white">NEXUS AI OS</div>
              <div className="text-xs text-gray-500">v1.0.0</div>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-end gap-1">
          <ThemeToggle />
          <NotificationBell />
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.path}
            onClick={() => router.push(item.path)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              pathname === item.path
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <span>🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}