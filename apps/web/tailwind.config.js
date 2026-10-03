/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        void: {
          DEFAULT: '#04060f',
          900: '#05070f',
          850: '#070b16',
          800: '#0a0f1e',
          700: '#0e1424',
        },
        navy: {
          800: '#0e1726',
          850: '#0b1320',
          900: '#080d1a',
          950: '#04070e',
        },
        cyber: {
          cyan: '#22d3ee',
          indigo: '#6366f1',
          violet: '#a855f7',
          teal: '#2dd4bf',
          purple: '#a855f7',
          emerald: '#34d399',
          amber: '#fbbf24',
          rose: '#fb7185',
        },
      },
      fontFamily: {
        sans: ['Satoshi', '"General Sans"', 'Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        display: ['"Clash Display"', '"Space Grotesk"', 'Satoshi', 'sans-serif'],
        head: ['"Clash Display"', 'Satoshi', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Fira Code', 'monospace'],
      },
      letterSpacing: {
        kicker: '0.28em',
      },
      borderRadius: {
        '2.5xl': '1.25rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'glow-cyan': '0 0 0 1px rgba(34,211,238,0.18), 0 10px 40px -12px rgba(34,211,238,0.45)',
        'glow-violet': '0 0 0 1px rgba(168,85,247,0.18), 0 10px 40px -12px rgba(168,85,247,0.45)',
        'panel': '0 24px 70px -32px rgba(0,0,0,0.9)',
        'inset-hair': 'inset 0 1px 0 0 rgba(255,255,255,0.06)',
      },
      backgroundImage: {
        'aurora': 'linear-gradient(120deg, #22d3ee 0%, #6366f1 42%, #a855f7 72%, #2dd4bf 100%)',
        'aurora-soft': 'linear-gradient(120deg, rgba(34,211,238,0.14), rgba(99,102,241,0.12) 45%, rgba(168,85,247,0.12))',
        'grid-fade': 'linear-gradient(rgba(148,163,184,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.045) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid-40': '40px 40px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-cyan': 'glowCyan 2s ease-in-out infinite alternate',
        'aurora-pan': 'auroraPan 18s ease infinite',
        'float-slow': 'floatSlow 7s ease-in-out infinite',
        'shimmer': 'shimmer 2.4s linear infinite',
        'sheen': 'sheen 6s ease-in-out infinite',
      },
      keyframes: {
        glowCyan: {
          '0%': { boxShadow: '0 0 5px rgba(34, 211, 238, 0.2), 0 0 10px rgba(34, 211, 238, 0.2)' },
          '100%': { boxShadow: '0 0 15px rgba(34, 211, 238, 0.6), 0 0 25px rgba(34, 211, 238, 0.4)' },
        },
        auroraPan: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        sheen: {
          '0%, 100%': { opacity: '0.35' },
          '50%': { opacity: '0.75' },
        },
      },
    },
  },
  plugins: [],
}
