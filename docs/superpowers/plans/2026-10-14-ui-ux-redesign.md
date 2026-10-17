# SIGEPSI UI/UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the SIGEPSI clinical platform (Web Angular 17 & Mobile Flutter) from flat solid colors into a premium, state-of-the-art UI featuring Aceternity UI style, Glassmorphism ("color cristales"), aurora radial gradients, Motion.dev spring micro-animations, and tactile cold buttons, while ensuring full system functionality and graceful handling of disabled email delivery.

**Architecture:** 
- Centralize CSS custom properties, glassmorphism utilities, cold button styles, and Motion.dev spring transitions in `prototipo/web/src/styles.css`.
- Update Angular web layout (`main-layout.component.ts`), dashboard, and authentication screens to consume glass panels and spring animations.
- Modernize Flutter mobile theme (`app_theme.dart`), login screen, and dashboard with `BackdropFilter`, frosted glass containers, and cold gradient buttons.
- Guarantee software verification across all three subprojects (`prototipo/web`, `prototipo/movil`, `prototipo/backend`) with strict evidence-based checks.

**Tech Stack:** 
- Web: Angular 17 (Standalone Components), TypeScript, Modern CSS3 (CSS Variables, `backdrop-filter`, spring cubic-beziers, keyframe stagger).
- Mobile: Flutter (Dart 3), Material 3, `BackdropFilter`, Google Fonts (Plus Jakarta Sans).
- Backend: Django 5 / Django REST Framework, Python 3.13.

**Spec:** [docs/superpowers/specs/2026-10-14-ui-ux-redesign-design.md](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/docs/superpowers/specs/2026-10-14-ui-ux-redesign-design.md)

## Global Constraints
- Brand palette preserved: Deep Forest (`#0b1e19`, `#0f2922`), Forest Green (`#19734e`), Mint Glow (`#2ec486`), Arctic Cold (`#0284c7`, `#38bdf8`).
- Strict WCAG 2.1 AA text contrast (minimum 4.5:1 for body and data text over frosted glass).
- Zero external package breaking changes in Angular; use pure modern CSS3 and native Angular lifecycle.
- Email sending (Gmail application password) is disabled by the user: any email sending or verification flow must fail gracefully or be bypassed without raising blocking 500 errors.
- Reduced motion: `@media (prefers-reduced-motion: reduce)` must be respected for all animations and spring transitions.

## Review Focus
1. **Low contrast on frosted backgrounds:** Text over semi-transparent white or dark glass must maintain 4.5:1 contrast against both the card and the underlying page background.
2. **Backdrop blur performance on mobile browsers:** Ensure `backdrop-filter` uses hardware acceleration with fallback solid background if blur is unsupported.
3. **Button interaction responsiveness:** Touch and click targets must be at least 44x44px with immediate visual feedback (`scale: 0.97`) without sluggish latency.
4. **Layout shifts during staggered animation load:** Pre-allocate card dimensions or use CSS `contain: layout` so entrance animations do not cause Cumulative Layout Shift (CLS < 0.1).
5. **Backend email dispatch crash prevention:** Background jobs or endpoints attempting `send_mail` must catch connection/auth errors cleanly and not disrupt user workflows.

---

### Task 1: Web Design System & Motion Tokens (`styles.css`)

**Files:**
- Modify: `prototipo/web/src/styles.css`
- Test: Build verification with Angular CLI

**Interfaces:**
- Produces: CSS utility classes:
  - `.glass-card`, `.glass-card-hover`
  - `.glass-panel`, `.glass-modal`
  - `.aurora-bg`, `.aurora-mesh`
  - `.btn-cold-primary`, `.btn-glass`, `.btn-shimmer`
  - `.badge-cold`, `.badge-mint-glow`
  - `--transition-spring`, `--transition-smooth`, `.animate-stagger-item`

- [ ] **Step 1: Write verification CSS tests / snapshot validation in styles.css**
Verify that existing base tokens are preserved while injecting the new glassmorphism and motion classes.

- [ ] **Step 2: Implement tokens and Aceternity/Glassmorphic classes in `prototipo/web/src/styles.css`**
Add:
- Glass variables: `--glass-bg-light`, `--glass-bg-dark`, `--glass-border`, `--glow-mint`, `--glow-cold`.
- Motion variables: `--transition-spring: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);`, `--transition-smooth: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);`.
- Tactile cold buttons: `.btn-cold-primary`, `.btn-glass`, `.btn-shimmer` with active press `transform: scale(0.97)`.
- Stagger entrance keyframes: `@keyframes fadeInUpStagger` with `--stagger-i` delay multiplier.
- Prefers-reduced-motion media query override.

- [ ] **Step 3: Run Angular build to verify CSS syntax and tokens**
Run: `npm run build` in `prototipo/web`
Expected: PASS with 0 build errors.

- [ ] **Step 4: Commit**
```bash
git add prototipo/web/src/styles.css
git commit -m "style(web): add glassmorphism, cold buttons, and motion.dev tokens"
```

---

### Task 2: Modernize Web Main Layout & Navigation (`main-layout.component.ts`)

**Files:**
- Modify: `prototipo/web/src/app/layout/main-layout.component.ts`

**Interfaces:**
- Consumes: `.glass-panel`, `.btn-cold-primary`, `.btn-glass`, `--transition-spring`
- Produces: Enhanced frosted sidebar, luminous active navigation pills, frosted header/user menu.

- [ ] **Step 1: Inspect current navigation styling and structure in `main-layout.component.ts`**
Check template and inline styles for `.app-sidebar`, `.nav-link`, `.sidebar-brand`, and `.top-bar`.

- [ ] **Step 2: Update sidebar and topbar styles to Aceternity Frosted Forest style**
- Transform `.app-sidebar` to frosted deep forest glass (`background: rgba(11, 30, 25, 0.85); backdrop-filter: blur(18px); border-right: 1px solid rgba(255, 255, 255, 0.08);`).
- Add luminous active pill with subtle mint glow (`background: linear-gradient(135deg, rgba(46, 196, 134, 0.18), rgba(25, 115, 78, 0.25)); border-left: 3px solid #2ec486; box-shadow: 0 0 16px rgba(46, 196, 134, 0.2);`).
- Apply spring micro-animations on nav links hover.
- Make top-bar and dropdown menus frosted glass surfaces.

- [ ] **Step 3: Verify Angular compilation**
Run: `npm run build` in `prototipo/web`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit**
```bash
git add prototipo/web/src/app/layout/main-layout.component.ts
git commit -m "style(web): modernize main layout with frosted glass sidebar and glowing navigation"
```

---

### Task 3: Redesign Web Dashboard & Login Screens

**Files:**
- Modify: `prototipo/web/src/app/modules/dashboard/dashboard.component.ts`
- Modify: `prototipo/web/src/app/modules/auth/login/login.component.ts`

**Interfaces:**
- Consumes: `.glass-card`, `.aurora-bg`, `.btn-cold-primary`, `.btn-shimmer`, `.animate-stagger-item`
- Produces: Modernized dashboard metric cards with glowing indicators and staggered entrance, frosted login card.

- [ ] **Step 1: Update `dashboard.component.ts` template and styles**
- Wrap stat metric cards in `.glass-card` with subtle radial gradient spotlight effect.
- Apply staggered animations (`style="--stagger-i: 1"`, etc.) for seamless entrance.
- Modernize action buttons to cold button styles (`.btn-cold-primary`, `.btn-glass`).

- [ ] **Step 2: Update `login.component.ts` template and styles**
- Transform login container into a frosted glass card centered over a subtle aurora mesh gradient.
- Modernize form inputs with glowing focus borders (`border-color: #2ec486; box-shadow: 0 0 0 3px rgba(46, 196, 134, 0.2)`).
- Upgrade submit button to cold primary button with tactile spring feedback.

- [ ] **Step 3: Verify Angular build**
Run: `npm run build` in `prototipo/web`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit**
```bash
git add prototipo/web/src/app/modules/dashboard/dashboard.component.ts prototipo/web/src/app/modules/auth/login/login.component.ts
git commit -m "style(web): apply glassmorphic cards and motion transitions to dashboard and login"
```

---

### Task 4: Modernize Mobile Flutter Theme & Core Components (`prototipo/movil`)

**Files:**
- Modify: `prototipo/movil/lib/core/theme/app_theme.dart`
- Modify: `prototipo/movil/lib/screens/login_screen.dart`
- Modify: `prototipo/movil/lib/screens/dashboard_screen.dart`

**Interfaces:**
- Produces: Glassmorphic decoration helpers in `AppTheme`, frosted glass login container, cold gradient CTA buttons, spring curves.

- [ ] **Step 1: Enhance `app_theme.dart` with glass decorations and spring curves**
- Add `glassDecoration` helper with subtle gradient and translucent borders.
- Add cold primary button style (`AppTheme.coldButton`).
- Define spring curve constants (`Curves.easeOutBack`, `Curves.easeInOutCubic`).

- [ ] **Step 2: Update `login_screen.dart`**
- Wrap the login form card in `BackdropFilter` with `ImageFilter.blur(sigmaX: 12, sigmaY: 12)`.
- Use translucent background (`Color(0xCC141C2E)`) and border (`0x332EC486`).
- Apply cold gradient button for login submission.

- [ ] **Step 3: Update `dashboard_screen.dart`**
- Upgrade metric cards to frosted glass style with glowing gradient borders.
- Add smooth animated entrance with `TweenAnimationBuilder` or `AnimatedContainer`.

- [ ] **Step 4: Verify Flutter analysis**
Run: `flutter analyze` in `prototipo/movil` (or Dart analysis)
Expected: 0 errors.

- [ ] **Step 5: Commit**
```bash
git add prototipo/movil/lib/core/theme/app_theme.dart prototipo/movil/lib/screens/login_screen.dart prototipo/movil/lib/screens/dashboard_screen.dart
git commit -m "style(movil): integrate glassmorphism, cold buttons and spring curves in Flutter app"
```

---

### Task 5: Backend Email-Safe Verification & Full System Integrity Check

**Files:**
- Inspect/Modify: `prototipo/backend/core/` and any email triggers if needed
- Test: `python manage.py check` in `prototipo/backend`
- Test: Full build and regression verification across `web`, `movil`, and `backend`

**Interfaces:**
- Consumes: All updated components
- Produces: System verification evidence proving the software works without blocking errors.

- [ ] **Step 1: Verify backend email safety**
Ensure backend services handle empty/invalid email settings gracefully (e.g. `send_mail(..., fail_silently=True)` or catching `SMTPAuthenticationError` / socket exceptions).

- [ ] **Step 2: Run Django system check**
Run: `python manage.py check` in `prototipo/backend`
Expected: System check identified no issues (0 silenced).

- [ ] **Step 3: Run comprehensive Web production build**
Run: `npm run build` in `prototipo/web`
Expected: Build successfully completed with 0 errors.

- [ ] **Step 4: Run Mobile code verification**
Run: `flutter analyze` in `prototipo/movil`
Expected: No errors.

- [ ] **Step 5: Commit**
```bash
git add prototipo/backend/
git commit -m "chore(backend): verify system integrity and safe email degradation"
```
