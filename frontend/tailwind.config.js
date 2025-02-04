export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
      extend: {
        colors: {
          accent: 'var(--accent)',
          secondary: 'var(--secondary)'
        },
        fontFamily: {
          mono: ['IBM Plex Mono', 'monospace']
        }
      }
    }
  }