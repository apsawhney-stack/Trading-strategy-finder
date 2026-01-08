## 2024-05-23 - Missing Screen Reader Utility
**Learning:** This repo's design system was missing the standard `.sr-only` utility class, forcing reliance on placeholders or aria-labels alone.
**Action:** Always check `index.css` or global styles first for accessibility utilities. Added standard `.sr-only` class to enable visually hidden but accessible labels, starting with the main URL input.
