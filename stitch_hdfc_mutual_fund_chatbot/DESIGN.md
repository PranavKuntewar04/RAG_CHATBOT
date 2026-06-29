---
name: Luminous Ledger
colors:
  surface: '#051424'
  surface-dim: '#051424'
  surface-bright: '#2c3a4c'
  surface-container-lowest: '#010f1f'
  surface-container-low: '#0d1c2d'
  surface-container: '#122131'
  surface-container-high: '#1c2b3c'
  surface-container-highest: '#273647'
  on-surface: '#d4e4fa'
  on-surface-variant: '#c5c6cd'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#8f9097'
  outline-variant: '#44474d'
  surface-tint: '#b9c7e4'
  primary: '#b9c7e4'
  on-primary: '#233148'
  primary-container: '#0a192f'
  on-primary-container: '#74829d'
  inverse-primary: '#515f78'
  secondary: '#bcc7de'
  on-secondary: '#263143'
  secondary-container: '#3e495d'
  on-secondary-container: '#aeb9d0'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#271500'
  on-tertiary-container: '#b67300'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#b9c7e4'
  on-primary-fixed: '#0d1c32'
  on-primary-fixed-variant: '#39475f'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
---

## Brand & Style
The design system is engineered for the high-stakes environment of mutual fund management, prioritizing institutional trust, clarity, and precision. The brand personality is authoritative yet technologically forward, designed to evoke a sense of calm reliability in the face of complex financial data.

The aesthetic follows a **Glassmorphic Modernism** approach. It utilizes deep, layered depth to organize information hierarchy. Surfaces are not solid; they are translucent panes that suggest a sophisticated digital ecosystem. This "layered intelligence" helps users distinguish between global navigation, account overviews, and granular transactional data without visual clutter. The emotional response should be one of "controlled transparency"—nothing is hidden, and the most important data is always elevated.

## Colors
The palette is rooted in a deep navy foundation to establish immediate professional gravity. 

- **Primary (#0A192F):** Used for the base background layer. It provides the "void" upon which all glass elements sit.
- **Secondary (#1E293B):** Used for component surfaces, cards, and navigation bars to create a subtle lift from the background.
- **Tertiary (#F59E0B):** Reserved strictly for warnings, pending states, or critical "action required" alerts. It is used sparingly to maintain high signal-to-noise ratios.
- **Accent (#38BDF8):** A bright sky blue used for primary actions, success states, and growth indicators (e.g., positive fund performance).
- **Neutral (#94A3B8):** Used for secondary text and icons to ensure the interface remains easy on the eyes during long sessions.

## Typography
The system uses **Inter** for its exceptional legibility in data-heavy contexts. The typographic scale is optimized for high-density information, such as portfolio tables and fund performance charts.

A secondary monospace font is introduced for numerical data and transaction IDs to ensure character alignment and prevent "jumping" during real-time data updates. Large headlines use tighter letter spacing to maintain a compact, professional appearance, while small labels use increased tracking for better readability on dark backgrounds.

## Layout & Spacing
The design system employs a **12-column fluid grid** for desktop and a **4-column grid** for mobile. A strict 8px spacing rhythm ensures mathematical harmony across all components.

Layouts should favor logical grouping over white space. In a fintech context, the user prefers to see more data "above the fold" than in a typical consumer app. Use horizontal dividers sparingly; instead, use background tonal shifts to separate content sections. On mobile, cards should extend full-width with a 16px safe-area margin to maximize the horizontal space for data tables and charts.

## Elevation & Depth
Depth is created through **Glassmorphism** and backdrop filters rather than traditional heavy shadows.

- **Level 0 (Background):** Solid Primary Navy (#0A192F).
- **Level 1 (Cards/Containers):** Secondary Slate (#1E293B) at 60% opacity with a `backdrop-filter: blur(12px)`.
- **Level 2 (Modals/Popovers):** Secondary Slate at 80% opacity with a `backdrop-filter: blur(20px)` and a subtle 1px inner border of white at 10% opacity to simulate a "glass edge."

Shadows, when used, are tinted with the primary navy color to avoid a "dirty" gray appearance. Use a 0px 4px 20px spread with 30% opacity for elevated elements.

## Shapes
This design system utilizes a "Soft" corner logic (4px - 12px radii). This strikes a balance between the rigid "sharp" look of traditional bank software and the overly "bubbly" look of consumer social apps. 

Containers use `rounded-lg` (8px), while primary action buttons use `rounded-xl` (12px) to make them more inviting to touch and interact with. Icons should follow a consistent 2px stroke weight with slightly rounded caps to match the UI's geometry.

## Components
- **Buttons:** Primary buttons are solid Sky Blue with white text. Secondary buttons use a "ghost" style with a 1px border. All buttons have a high-gloss hover state that increases backdrop-blur intensity.
- **Data Cards:** These are the workhorses of the UI. They must include a subtle 1px top-border gradient (white to transparent) to catch the "light" and define the top edge of the pane.
- **Input Fields:** Fields are dark-recessed with a 1px border that glows Sky Blue on focus. Error states swap the glow to the Warning Yellow (#F59E0B).
- **Performance Chips:** Small, pill-shaped indicators for percentage growth. Positive values use a low-opacity green background; negative values use a low-opacity red.
- **Financial Charts:** Use thin line weights (1.5pt) for trend lines. Area charts should use a vertical gradient from the stroke color to transparent to maintain the glass aesthetic.
- **Steppers:** Used for multi-step investment flows (KYC, SIP setup). Steppers are horizontal on desktop and vertical on mobile, utilizing a "dimmed out" state for future steps to focus the user's attention.