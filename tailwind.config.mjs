/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        parchment:  '#f5f4ed',
        ivory:      '#faf9f5',
        'warm-sand': '#e8e6dc',
        brand: {
          DEFAULT:  '#1B365D',
          light:    '#2D5A8A',
          tint:     '#EEF2F7',
        },
        'near-black': '#141413',
        'dark-warm':  '#3d3d3a',
        olive:       '#504e49',
        stone:       '#6b6a64',
        border:      '#e8e6dc',
        'border-soft': '#e5e3d8',
      },
      fontFamily: {
        serif: [
          '"Source Han Serif SC"',
          '"Noto Serif CJK SC"',
          '"Songti SC"',
          '"STSong"',
          'Georgia',
          'serif',
        ],
        mono: [
          '"JetBrains Mono"',
          '"SF Mono"',
          'Consolas',
          'monospace',
        ],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: '100%',
            color: theme('colors.near-black'),
            lineHeight: '1.65',
            letterSpacing: '0.3px',
            h1: { color: theme('colors.brand.DEFAULT'), fontWeight: '500' },
            h2: { color: theme('colors.brand.DEFAULT'), fontWeight: '500' },
            h3: { color: theme('colors.brand.DEFAULT'), fontWeight: '500' },
            h4: { color: theme('colors.brand.DEFAULT'), fontWeight: '500' },
            a: { color: theme('colors.brand.DEFAULT'), textDecoration: 'none' },
            'a:hover': { textDecoration: 'underline' },
            blockquote: {
              borderLeftColor: theme('colors.brand.DEFAULT'),
              color: theme('colors.olive'),
              fontStyle: 'normal',
              quotes: 'none',
            },
            code: {
              color: theme('colors.brand.DEFAULT'),
              backgroundColor: theme('colors.brand.tint'),
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '0.9em',
            },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
            pre: {
              backgroundColor: '#1e1e1e',
              color: '#d4d4d4',
            },
            img: {
              borderRadius: '8px',
              boxShadow: '0 2px 12px rgba(27,54,93,0.08)',
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
