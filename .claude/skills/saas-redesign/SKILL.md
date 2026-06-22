---
name: saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface — vertical left sidebar navigation, a single design-token system (colors, spacing, typography, radii, content width), and a polished professional look inspired by Linear, shadcn, v0, and Legora with natural tones and sharp, thin edges. Use when asked to redesign, restyle, modernize, or make the UI consistent, or to add a sidebar layout.
---

# SaaS UI Redesign

Transform the app from an ad-hoc styled top-nav layout into a token-driven, sidebar-based SaaS interface. The end state is: **one place defines every color, spacing step, font size, radius, and content width — every component consumes tokens, nothing redefines them.**

## Design direction

Reference points: **Linear** (density, restraint, hairline borders), **shadcn/ui** (token discipline, neutral surfaces), **v0** (clean composition), **Legora** (calm, professional, content-first). Adapt the direction, don't copy:

- **Natural tones over cool grays.** Warm stone/sand neutrals for surfaces and text, one muted moss-green accent. No saturated blues/purples as the primary accent. Status colors stay but are desaturated.
- **Sharp, thin edges over heavy rounding.** 1px hairline borders carry the structure; shadows are nearly absent (only menus/modals get one). Radii are small: 3–6px for almost everything, 8px max for modals. Never 10px+, never pill-shaped buttons.
- **Quiet typography.** One typeface (Inter), weights 400/500/600 only (700 reserved for the page title at most), a fixed 6-step type scale, `tabular-nums` on all numeric/data cells.
- **Density and alignment.** Consistent 4px-based spacing scale, one content max-width, one page padding. Whitespace is uniform, not generous in one view and cramped in the next.
- **No decoration.** No gradients, no emojis in UI, no icon noise — text labels in the sidebar are enough (a small inline SVG icon set is acceptable if added consistently to every nav item).

The full token sheet (CSS custom properties with exact values) is in [reference/tokens.css](reference/tokens.css). The sidebar shell markup/CSS template is in [reference/sidebar-layout.md](reference/sidebar-layout.md).

## Workflow

Work in this order. Do not restyle individual views before the tokens and shell exist — that recreates the inconsistency the skill exists to remove.

### 1. Audit

Quantify the current sprawl so you know what must converge and can prove convergence at the end:

```bash
# Distinct hardcoded colors
grep -rEoh '#[0-9a-fA-F]{3,8}' client/src --include="*.vue" --include="*.css" | sort | uniq -c | sort -rn
# Distinct radii
grep -rEoh 'border-radius:\s*[^;]+' client/src --include="*.vue" | sort | uniq -c | sort -rn
# Distinct font sizes / families
grep -rEoh 'font-(size|family):\s*[^;]+' client/src --include="*.vue" | sort | uniq -c | sort -rn
# Per-view max-widths and paddings on page containers
grep -rn 'max-width\|padding:' client/src/views client/src/App.vue | head -50
```

Also list every view and component, and note which global classes already exist (`.card`, `.stat-card`, `.badge`, table styles, etc. — in this project they live in `App.vue`'s unscoped `<style>` block). Record the baseline numbers; the verification step compares against them.

### 2. Establish the token layer

Create `client/src/styles/tokens.css` from [reference/tokens.css](reference/tokens.css) and import it first in `main.js` (before any component). All values are CSS custom properties on `:root`.

Rules for this layer:

- It is the **only** file allowed to contain raw hex colors, the font-family stack, and radius/spacing literals.
- Keep the existing semantic class names the views already use (`.card`, `.stat-card`, `.badge.success`, `.page-header`, table styles, `.loading`, `.error`). Re-implement them on top of the tokens in a global stylesheet (either keep them in `App.vue`'s unscoped style block or move them to `client/src/styles/base.css` imported after tokens). Renaming shared classes forces touching every template — don't, unless a name is actively misleading.
- Status colors map through semantic tokens (`--color-success`, `--color-warning`, `--color-danger`, `--color-info`) plus their `-bg` surface variants — components never pick their own greens/reds.

### 3. Replace the top nav with a sidebar shell

Rework the root layout (`client/src/App.vue`) following [reference/sidebar-layout.md](reference/sidebar-layout.md):

- Fixed left sidebar (`--sidebar-width`, 240px): product name at top, vertical nav links (the existing router-links), utility items (language switcher, profile) pinned at the bottom.
- Main column to the right: a slim sticky topbar (page title area + the existing `FilterBar` content), then the scrollable content region with `--content-max-width` and `--content-padding`.
- Active nav item: accent-tinted background + accent text, small radius — no underline bars, no left border strips.
- Keep all existing behavior (router links, modals, FilterBar logic, composables) — this is a layout and style change only, not a refactor of component logic.
- Below `--breakpoint-collapse` (1024px) the sidebar collapses to icons-or-hidden with a toggle; don't build a separate mobile nav system.

### 4. Migrate views and components to tokens

Go view by view (then modals/components). For each file:

1. Replace every hardcoded color, font-size, font-weight, radius, spacing, and shadow in scoped styles with the corresponding `var(--…)` token. If a value has no matching token, snap it to the nearest token — do not add a new one without a strong reason (and if added, it goes in `tokens.css`, never inline).
2. Delete scoped styles that duplicate a global class (`.card`, `.badge`, table styles, stat cards) and use the global class instead. Per-view "almost the same card" styles are the main source of drift.
3. Remove per-view `max-width`, page-level padding, and page-header styling — the shell owns those.
4. Charts (custom SVG) use token colors via `var()` in fills/strokes; keep the existing chart structure.
5. Apply `font-variant-numeric: tabular-nums` (global utility class) to numeric table columns and stat values.

**Anti-sprawl rules while migrating:**
- Do not create new components for one-off styling; restyle in place. Create a shared component only when the same markup+style block appears in 3+ places.
- Do not introduce a CSS framework, UI library, or new dependency — this is a token + hand-rolled CSS system.
- Every modal uses the same overlay, panel width step, header, and close-button treatment.
- Buttons come in exactly three variants (primary = accent, secondary = outlined neutral, ghost) and two sizes; badges in one size.

Respect this project's delegation rule: creating or significantly modifying `.vue` files is done via the **vue-expert** subagent (see CLAUDE.md). Give it the token file and these rules as context in the prompt so it doesn't reinvent values.

### 5. Verify and enforce

Re-run the audit greps from step 1 and compare:

- Raw hex colors outside `tokens.css`: target **0** (allow only `#fff`/`currentColor` edge cases if justified).
- `border-radius` literals outside `tokens.css`: 0 — everything via `var(--radius-*)`.
- `font-family` declarations outside `tokens.css`: 0.
- Distinct font-size values: only the 6 scale steps.
- One `max-width` for content, defined once in the shell.

Then verify visually: start the app (frontend on `http://localhost:3000`, backend on `:8001`) and use the Playwright MCP tools to screenshot every route (`/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`) plus at least one open modal. Check: sidebar renders on every route, active state tracks the route, no horizontal scroll at 1280px and 1440px, tables/cards/badges look identical across views, and nothing still shows the old blue accent or heavy rounded corners. Fix regressions before reporting done.

Report the before/after audit numbers (distinct colors, radii, font sizes) as the proof of convergence.
