'use client';

import { useTheme } from './ThemeProvider';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 text-gray-400 hover:text-white transition-colors"
      title={theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
    >
      <span className="text-xl">{theme === 'dark' ? '☀️' : '🌙'}</span>
    </button>
  );
}