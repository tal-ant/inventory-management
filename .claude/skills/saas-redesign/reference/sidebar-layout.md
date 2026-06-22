# Sidebar shell template

Target structure for the root layout (`App.vue` in this project). Keep existing
component logic (router links, FilterBar, modals, composables) — only the layout
and styling change. All values come from `tokens.css`; no literals here are
authoritative except where they reference a token.

## Structure

```
┌──────────────┬──────────────────────────────────────────────┐
│ sidebar      │ topbar (sticky): page title · FilterBar · …  │
│  product     ├──────────────────────────────────────────────┤
│  ── nav ──   │                                              │
│  Overview    │   content (scrolls, max-width, centered)     │
│  Inventory   │     <router-view />                          │
│  Orders      │                                              │
│  Finance     │                                              │
│  Demand      │                                              │
│  Reports     │                                              │
│  ── footer ──│                                              │
│  Lang · User │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

## Template skeleton

```vue
<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" :class="{ active: $route.path === '/' }">{{ t('nav.overview') }}</router-link>
        <router-link to="/inventory" :class="{ active: $route.path === '/inventory' }">{{ t('nav.inventory') }}</router-link>
        <!-- …remaining routes, same pattern… -->
      </nav>

      <div class="sidebar-footer">
        <LanguageSwitcher />
        <ProfileMenu @show-profile-details="…" @show-tasks="…" />
      </div>
    </aside>

    <div class="main-column">
      <header class="topbar">
        <FilterBar />
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>

    <!-- modals stay where they are -->
  </div>
</template>
```

## CSS skeleton

```css
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* Sidebar ------------------------------------------------------------ */
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: var(--border-width) solid var(--color-border);
  padding: var(--space-5) var(--space-3);
}

.sidebar-brand {
  padding: 0 var(--space-3) var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.brand-name {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  letter-spacing: var(--tracking-tight);
}
.brand-sub {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.sidebar-nav a {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}
.sidebar-nav a:hover {
  background: var(--color-surface-sunken);
  color: var(--color-text);
}
.sidebar-nav a.active {
  background: var(--color-accent-soft);
  color: var(--color-accent-text);
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding-top: var(--space-4);
  border-top: var(--border-width) solid var(--color-border);
}

/* Main column --------------------------------------------------------- */
.main-column {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: var(--topbar-height);
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border-bottom: var(--border-width) solid var(--color-border);
  padding: 0 var(--content-padding);
}

.content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--content-padding) var(--space-12);
}

/* Collapse ------------------------------------------------------------ */
@media (max-width: 1024px) { /* keep in sync with --breakpoint-collapse */
  .sidebar { transform: translateX(-100%); transition: transform var(--transition-base); }
  .sidebar.open { transform: translateX(0); box-shadow: var(--shadow-overlay); }
  .main-column { margin-left: 0; }
  /* add a hamburger toggle in .topbar that toggles .open */
}
```

## Notes

- The active state is background + text color only — no underline bars,
  no left accent strips, no bold-on-active weight changes.
- `.page-header` inside views shrinks: title at `--text-lg`, optional one-line
  description in `--color-text-muted`; the heavy 1.875rem headers go away.
- The topbar holds the FilterBar; if a view needs a page-level action button,
  it goes at the right end of the topbar, not floating inside the content.
- z-index order: topbar 50, sidebar 60 (when overlaying at small widths),
  dropdown menus 100, modal overlays 200. Define once, reuse.
