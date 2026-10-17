# Design Document: SIGEPSI UI/UX Redesign (Aceternity UI & Glassmorphism)

**Date:** 2026-10-14  
**Author:** Pair Programming Agent & User  
**Status:** In Review  
**Target Systems:** `prototipo/web` (Angular 17), `prototipo/movil` (Flutter), `prototipo/backend` (Django REST API verification)

---

## 1. Intent & The Why

The SIGEPSI clinical psychological platform currently uses a solid, flat color palette. While functionally sound, the interface feels heavy, monolithic, and lacking depth or modern tactile micro-interactions. 

The goal of this redesign is to elevate the visual experience across both Web and Mobile platforms into a premium, state-of-the-art UI inspired by modern libraries like **Aceternity UI**, featuring **Glassmorphism ("color cristales")**, **radiant aurora gradients**, and **tactile "cold buttons" with subtle glow accents**, while strictly preserving the trusted clinical brand identity (Forest Green & Vibrant Mint) and all underlying business logic and clinical security.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **Modern Glassmorphic Visual Language:** Implement multi-layered translucent glass panels (`backdrop-filter: blur(...)`), subtle light-reflecting borders (`1px solid rgba(255, 255, 255, 0.25)` or `rgba(46, 196, 134, 0.2)`), and smooth ambient shadows.
- **Radiant Aurora Gradients:** Replace flat backgrounds and solid banners with subtle radial/mesh aurora lighting that adds depth without causing visual fatigue.
- **Cold Interactive Buttons & Accents ("Botones Fríos"):**
  - Primary button: crisp mint-to-emerald gradient with a luminous halo on hover.
  - Secondary button: frosted glass with light borders and smooth elevation.
  - Shimmer effect button: subtle light-beam animation across borders or surfaces for primary calls to action.
- **Motion.dev Spring Physics & Micro-Animations:**
  - Modern spring animations (`cubic-bezier(0.34, 1.56, 0.64, 1)` / spring physics) for tactile button clicks (`active: scale(0.97)`).
  - Staggered entrance animations for dashboard stat cards and lists (smooth fade-up with progressive delays).
  - Ambient glowing pulses for active states and live indicators.
  - Full respect for `prefers-reduced-motion: reduce` to ensure accessible, non-disruptive UX.
- **Cross-Platform Consistency:**
  - **Web (Angular 17):** Update design tokens in `styles.css`, modern sidebar with glowing active pills, glass cards for dashboard/clinical charts/tables, modal dialogues with backdrop blur.
  - **Móvil (Flutter):** Integrate `BackdropFilter` glass containers, gradient cards, frosted bottom navigation, and cold-glow action buttons.
- **Flawless Software Verification:** Run build checks (`ng build`, flutter analyze, Django test suite) to guarantee no regressions or broken functionality.

### Non-Goals
- Changing clinical business logic, database models, or API endpoints.
- Rewriting routing or component state machines.
- Creating full new clinical features beyond the visual/interaction redesign.

### Anti-Goals (What would make this a failure)
- Breaking clinical usability or legibility (contrast must strictly meet WCAG 4.5:1 for body and data text).
- Over-animating or causing layout lag / GPU thrashing.
- Altering the email/Gmail sending logic that was intentionally disabled by the user (do not attempt to re-enable or fail on email auth).

---

## 3. Constraints

- **Email Subsystem:** The Gmail application password has been disabled by the user. Any verification or runtime path must gracefully handle or bypass email sending without throwing blocking exceptions.
- **No Heavy External UI Frameworks that break Angular 17 standalone architecture:** Aceternity concepts will be implemented using pure modern CSS3 (custom properties, backdrop-filter, keyframes, radial-gradients) and Angular animations to ensure maximum performance and zero dependency overhead.
- **Flutter Compatibility:** Flutter mobile design must use native widgets (`BackdropFilter`, `BoxDecoration` gradients, `BoxShadow` with blur radius) matching `Material 3` without breaking Dart 3 SDK constraints.

---

## 4. Visual Architecture & Design Decisions

### 4.1 Design System Tokens (`styles.css` / `AppTheme.dart`)
- **Brand Palette:**
  - Deep Forest (Canvas/Sidebar Dark): `#0b1e19` / `#0f2922`
  - Forest Primary: `#19734e`
  - Vibrant Mint (Active/Glow): `#2ec486` / `#34d399`
  - Arctic Cold Accent (Secondary Glow): `#0284c7` / `#38bdf8`
  - Off-White Canvas Surface: `#f4f7f5` with translucent overlay
- **Glass Token Hierarchy:**
  - `--glass-bg-light`: `rgba(255, 255, 255, 0.75)` with `backdrop-filter: blur(16px)`
  - `--glass-bg-dark`: `rgba(11, 30, 25, 0.75)` with `backdrop-filter: blur(18px)`
  - `--glass-border`: `1px solid rgba(255, 255, 255, 0.35)`
  - `--glass-border-accent`: `1px solid rgba(46, 196, 134, 0.3)`
  - `--glow-mint`: `0 0 20px rgba(46, 196, 134, 0.35)`
  - `--glow-cold`: `0 0 20px rgba(14, 165, 233, 0.30)`

### 4.2 Motion.dev Animation System & Transitions
- **Spring Transition Curves:** `--transition-spring: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);` for elastic bounce on hover and press.
- **Smooth Surface Transitions:** `--transition-smooth: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);` for glass panels and color fades.
- **Stagger Animations:** CSS staggered keyframes `@keyframes fadeInUpStagger` with `animation-delay: calc(var(--stagger-i, 0) * 80ms)` for sequential card loading.
- **Active Tactile Feedback:** Buttons and interactive cards slightly scale to `0.97` on pointerdown/active and bounce back on release.
- **Accessibility:** `@media (prefers-reduced-motion: reduce)` disables scale bounces and sets transitions to 0s to guarantee safety and compliance.

### 4.3 Web Components to Update
1. **`src/styles.css`**: Core design tokens, glassmorphism utilities (`.glass-card`, `.glass-panel`, `.glass-modal`, `.btn-cold-primary`, `.btn-glass`, `.btn-shimmer`, `.glow-badge`), aurora gradient mesh helpers.
2. **`src/app/layout/main-layout.component.ts`**: Sidebar in frosted deep forest glass, luminous active link pill with mint glow, user profile dropdown and topbar with frosted glass effect.
3. **`src/app/modules/dashboard/dashboard.component.ts`**: Metric cards with radial gradient accents, quick action buttons, high-contrast readable charts.
4. **`src/app/modules/auth/login/login.component.ts`**: Modern frosted login card with subtle glowing perimeter and aurora backdrop.

### 4.3 Mobile Components to Update
1. **`lib/core/theme/app_theme.dart`**: Integrate glassmorphism theme helpers, cold button styles, border gradients, and elevation shadows.
2. **`lib/screens/login_screen.dart`**: Frosted glass container card with ambient background glow.
3. **`lib/screens/dashboard_screen.dart`**: Glass stat tiles, cold CTA buttons, and sleek clinical navigation.

---

## 5. Verification Strategy

Following `verification-before-completion`:
1. **Web Build Verification:** Run `npm run build` in `prototipo/web` to guarantee 0 TypeScript/CSS build errors.
2. **Mobile Code Analysis:** Run `flutter analyze` or Dart analyzer in `prototipo/movil`.
3. **Backend Health Check:** Run Django system checks (`python manage.py check`) in `prototipo/backend`.
4. **Email Safety:** Verify that operations requiring notifications do not raise unhandled errors when email credentials are blank/inactive.

---

## 6. What's Left to the Builder

- Fine-tuning exact pixel margins and transition cubic-beziers (`cubic-bezier(0.4, 0, 0.2, 1)`) for micro-interactions.
- Ensuring mobile responsive breakpoints at 375px, 768px, 1024px, and 1440px.
