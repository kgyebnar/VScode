export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        status: {
          pending: '#94a3b8',
          running: '#3b82f6',
          completed: '#10b981',
          failed: '#ef4444',
          paused: '#f59e0b',
          skipped: '#8b5cf6',
        }
      }
    },
  },
  plugins: [],
}
