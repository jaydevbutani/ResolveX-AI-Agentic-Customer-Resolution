---
name: Kinetic Obsidian & Alabaster
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#45474b'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#76777b'
  outline-variant: '#c6c6cb'
  surface-tint: '#5c5e64'
  primary: '#04060a'
  on-primary: '#ffffff'
  primary-container: '#1c1f24'
  on-primary-container: '#84868d'
  inverse-primary: '#c4c6cd'
  secondary: '#476800'
  on-secondary: '#ffffff'
  secondary-container: '#bcf063'
  on-secondary-container: '#4b6d00'
  tertiary: '#050411'
  on-tertiary: '#ffffff'
  tertiary-container: '#1e1d2c'
  on-tertiary-container: '#878497'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e1e2e9'
  primary-fixed-dim: '#c4c6cd'
  on-primary-fixed: '#191c21'
  on-primary-fixed-variant: '#44474c'
  secondary-fixed: '#bff365'
  secondary-fixed-dim: '#a4d64c'
  on-secondary-fixed: '#131f00'
  on-secondary-fixed-variant: '#354e00'
  tertiary-fixed: '#e4e0f5'
  tertiary-fixed-dim: '#c7c4d8'
  on-tertiary-fixed: '#1b1a29'
  on-tertiary-fixed-variant: '#464555'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.03em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Space Grotesk
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.25rem
---

## Brand & Style

This design system fuses high-end editorial clarity with an engineered, modern telemetry feel. It pairs an architectural dark-slate containment shell with an ultra-clean, luminous light-canvas workspace. The emotional response is intentional, energetic, and commanding—instilling immediate focus and confidence without eye strain.

The design movement synthesizes Swiss editorial grotesque discipline (inspired by industrial logistics layouts) with dynamic soft-modular dashboard design. Key brand characteristics:
- **Framed Immersion:** Structural obsidian framing provides stable peripheral orientation, allowing the core content canvas to float with light, calm clarity.
- **Electric Accents:** Energetic lime and chartreuse sparks draw direct focus to key metrics, active states, and calls to action without visual clutter.
- **Editorial Legibility:** Razor-sharp typography and generous micro-spacing guarantee rapid data absorption and high-contrast readability across all surfaces.

## Colors

The palette establishes an asymmetrical visual structure that uses both dark frame tokens and light workspace tokens seamlessly.

- **Primary (`#1c1f24`):** Deep obsidian charcoal. Serves as the navigation chassis, primary application frame, inverted hero tiles, and highest-priority interactive toggles.
- **Secondary (`#bef264`):** Vibrant electric chartreuse/lime. Used deliberately for focal highlights, active pill badges, progress indicator terminals, and conversion drivers.
- **Tertiary (`#ede9fe`):** Soft pastel iris/lavender. Functions as a secondary data visualization marker, balanced category tag, and subtle selection fill.
- **Neutral (`#0f172a`):** Deep slate-black. Delivers uncompromising typographical contrast on light canvas cards, paired with neutral utility grays:
  - Surface Background: `#f3f4f6` (warm off-white foundation canvas)
  - Card & Container Surface: `#ffffff` (crisp elevated modular cards)
  - Subtle Border: `#e2e8f0` (gentle division lines)
  - Muted Text: `#64748b` (secondary labels and metadata)

Dark surfaces use white typography (`#ffffff`) and secondary text in light cool gray (`#94a3b8`), preserving maximum contrast ratio thresholds above 7:1.

## Typography

The type system blends the industrial, technical authority of **Space Grotesk** with the ergonomic human-centric clarity of **Plus Jakarta Sans**.

- **Space Grotesk** governs all primary titles, telemetry readouts, metric integers, chart callouts, and interactive button labels. Its geometric stance delivers structural confidence reminiscent of modern logistics interfaces.
- **Plus Jakarta Sans** provides continuous readability across running copy, user settings, field placeholders, and tabular descriptions without visual fatigue.
- Metrics and numeric figures are prioritized: use tight negative letter-spacing for headline sizes to form monolithic, scan-friendly units.

## Layout & Spacing

The architectural layout utilizes a persistent peripheral master navigation frame (dark slate `#1c1f24`) wrapped around a 12-column responsive grid workspace canvas (`#f3f4f6`).

- **Desktop (1024px+):** Fixed 260px dark navigation sidebar flanking an expansive fluid main canvas with a 24px default inner grid gutter and 32px canvas margins. Cards distribute dynamically across 3, 4, 6, or 12 column modules.
- **Tablet (768px - 1023px):** Collapsed 72px icon-only vertical sidebar rail, 20px gutters, and 24px margins. Modular cards collapse from 4 columns to 2-column stacked pairs.
- **Mobile (<768px):** The dark frame transitions into an elevated bottom navigation bar or slide-out overlay drawer. The canvas margin tightens to 16px, gutters down to 16px, with content stacking in a singular column.

Component density is governed by strict multiples of 4px, emphasizing comfortable inner padding (20px to 28px) inside metric cards to prevent visual crowding.

## Elevation & Depth

Visual hierarchy uses a crisp layered-plane strategy instead of muddy drop shadows:

1. **Base Frame (Level 0):** Obsidian Dark (`#1c1f24`), flush and solid. Houses global navigation, search roots, and quick-action utility docks.
2. **Main Workspace Canvas (Level 1):** Matte off-white foundation (`#f3f4f6`), recessed slightly by the surrounding dark frame.
3. **Card & Widget Surfaces (Level 2):** Pure stark white (`#ffffff`) planar islands elevated by an ultra-soft, diffuse shadow: `0 8px 24px -4px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02)`. A 1px hairline border in `#edf2f7` preserves edge definition against high-brightness displays.
4. **Accent Dark Panels (Level 2 Inverted):** Selected summary units (e.g., trend charts or night telemetry) adopt `#1c1f24` fills directly within the light canvas, maintaining parity with the outer frame.
5. **Floating Overlays & Menus (Level 3):** Clean white cards with `0 16px 36px -6px rgba(15, 23, 42, 0.08)` and subtle border strokes.

## Shapes

The design system employs a rounded, friendly geometry grounded by architectural corners:
- Standard widgets, cards, and segmented content panels: `rounded-lg` (16px / 1rem).
- Outer dashboard container shell: `rounded-xl` (24px / 1.5rem) where framed inside viewport windows.
- Badges, status chips, quick toggles, and main action buttons: Fully curved pill shape (`rounded-full` / 9999px) for ergonomic distinction.
- Inputs and nested table cells: `rounded` (8px / 0.5rem) to preserve structured data rows.

## Components

### Buttons
- **Primary Action:** Solid obsidian `#1c1f24` background with pure white `#ffffff` text, or high-conversion electric chartreuse `#bef264` with black `#0f172a` text. Fully rounded pill contour (`rounded-full`), `space-sm` vertical by `space-lg` horizontal padding, paired with `label-lg` typography.
- **Secondary / Ghost:** Transparent base with `#e2e8f0` border, `#0f172a` text, shifting to a `#f1f5f9` hover fill.
- **Inverted Dark-Frame Action:** High-contrast lime `#bef264` interactive button with black typography inside dark sidebar panels.

### Chips & Badges
- **Status Indicators:** Pill-shaped elements with `space-xs` vertical and `space-sm` horizontal padding.
- **Lime Accent Chip:** Faint lime tint `#f7fee7` with `#3f6212` text and bold metric tags (`+5%`, `Active`).
- **Iris Chip:** `#ede9fe` background with `#5b21b6` text for secondary classifications.
- **Dark Pill Count:** Charcoal `#1c1f24` with secondary lime `#bef264` count badges.

### Metric & Telemetry Cards
- **Light Metric Cards:** `#ffffff` surface, 24px inner padding, containing a distinct header row (icon, metric title in `body-sm`, and contextual three-dot overflow). Metrics utilize `Space Grotesk` at `headline-lg` (32px), with micro delta tags anchored to their top-right.
- **Inverted Focus Card:** Obsidian `#1c1f24` background with crisp white typography, housing high-contrast vertical bar charts, chartreuse lead bars, and lavender comparative bars.

### Lists & Activity Rows
- Minimal borderless rows with `12px` vertical padding. Left-aligned avatars or rounded icon squares (40px) with subtle gray backgrounds, middle label/sublabel stack, and right-aligned numeric indicators. Bottom hairline division using `#f1f5f9`.

### Input Fields & Controls
- **Search & Text Inputs:** Pill or 12px rounded forms with `#ffffff` backgrounds, subtle `#e2e8f0` outer strokes, and `body-md` typography. On focus, apply a crisp 2px chartreuse focus ring (`#bef264`).
- **Checkboxes & Radios:** Custom 20px rounded controls. Active states fill with primary `#1c1f24` featuring crisp white check indicators or chartreuse accents.

### Toggle Segments
- Encapsulated pills in soft gray `#e2e8f0` track wrappers containing sliding white pills for active states, maintaining legible `label-md` type contrast.