# Palette's Journal

## 2025-02-14 - Accessibility Labels
**Learning:** Placeholders are not accessible labels. Screen readers may skip them, and they disappear when typing.
**Action:** Always add `aria-label` or visible `<label>` to inputs, even if the design relies on placeholders.

## 2025-02-14 - Icon-only Buttons
**Learning:** Buttons with only text content like "✕" or emojis are often read literally (e.g., "Multiplication Sign") or ignored by screen readers.
**Action:** Always provide an explicit `aria-label` for icon-only buttons to describe the action (e.g., "Close", "Delete").
