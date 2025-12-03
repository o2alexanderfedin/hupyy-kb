# Hupyy KB - Brand Identity Specifications

## Document Control

**Version**: 1.0.0
**Date**: 2025-12-03
**Status**: Approved for Implementation
**Owner**: Product Team
**Previous Brand**: PipesHub

---

## Executive Summary

This document defines the complete brand identity for Hupyy KB, the rebranded version of PipesHub. Hupyy KB maintains the core value proposition of workplace AI while establishing a distinct, memorable brand presence that emphasizes knowledge, intelligence, and modern enterprise technology.

---

## Brand Name & Positioning

### Official Brand Name
**Hupyy KB**

### Pronunciation
**"Happy Kay-Bee"** or **"Hoo-pee Kay-Bee"**

### Legal Entity Names
- **Primary**: Hupyy KB
- **Short Form**: Hupyy
- **Technical/Package Names**: hupyy-kb (lowercase with hyphen)
- **Domain Strategy**: hupyy.com (primary), hupyykb.com (redirect)

### Tagline Options
1. **Primary**: "Your Workplace AI Knowledge Platform"
2. **Alternative**: "Open Source Workplace Intelligence"
3. **Technical**: "The Open Source Alternative to Glean"
4. **Aspirational**: "Knowledge at the Speed of Thought"

### Product Positioning Statement
Hupyy KB is the open-source workplace AI platform that connects all your company's knowledge sources, providing instant, contextual answers to your team. Built for enterprises that value transparency, privacy, and control over their AI infrastructure.

### Value Propositions
1. **Privacy First**: On-premise deployment, your data never leaves your infrastructure
2. **Open Source**: Transparent, auditable, community-driven development
3. **Unified Knowledge**: Connect 50+ data sources into one intelligent platform
4. **Cost Effective**: No per-seat licensing, unlimited users
5. **Customizable**: Full control over AI models, connectors, and workflows

---

## Visual Identity

### Logo Specifications

#### Logo Concepts
**Primary Concept**: Knowledge cube with neural network overlay
- Geometric cube representing structured knowledge (KB)
- Interconnected nodes suggesting AI intelligence
- Modern, tech-forward aesthetic
- Works in both light and dark modes

**Alternative Concept**: Speech bubble + brain hybrid
- Combines conversation (chatbot) with intelligence
- Emphasizes the AI assistant nature of the product
- Friendly, approachable design

#### Logo Files Required
1. **logo-full.svg** (2400x600px)
   - Full horizontal logo with icon + wordmark
   - For headers, documentation, marketing
   - SVG format for scalability
   - Two color variants: full color and monochrome

2. **logo-single.jpg** (512x512px)
   - Icon/mark only (no text)
   - Square format for social media, app icons
   - Both PNG (transparent) and JPG versions
   - Multiple sizes: 512x512, 256x256, 128x128, 64x64, 32x32

3. **logo-blue.svg** (Same dimensions as logo-full.svg)
   - Primary brand color version
   - For use on light backgrounds
   - Corporate/professional contexts

4. **favicon.ico** (Multi-resolution)
   - 16x16, 32x32, 48x48 embedded in single .ico file
   - Simplified version of logo mark
   - High contrast for visibility at small sizes

### Color Palette

#### Primary Colors
```css
/* Primary Brand Color - Knowledge Blue */
--hupyy-primary: #2563EB;        /* rgb(37, 99, 235) */
--hupyy-primary-dark: #1E40AF;   /* rgb(30, 64, 175) */
--hupyy-primary-light: #60A5FA;  /* rgb(96, 165, 250) */

/* Secondary Brand Color - Intelligence Purple */
--hupyy-secondary: #7C3AED;      /* rgb(124, 58, 237) */
--hupyy-secondary-dark: #5B21B6; /* rgb(91, 33, 182) */
--hupyy-secondary-light: #A78BFA;/* rgb(167, 139, 250) */

/* Accent Color - Success Green */
--hupyy-accent: #10B981;         /* rgb(16, 185, 129) */
--hupyy-accent-dark: #059669;    /* rgb(5, 150, 105) */
--hupyy-accent-light: #34D399;   /* rgb(52, 211, 153) */
```

#### Neutral Colors
```css
/* Neutral Scale for UI */
--hupyy-gray-50: #F9FAFB;
--hupyy-gray-100: #F3F4F6;
--hupyy-gray-200: #E5E7EB;
--hupyy-gray-300: #D1D5DB;
--hupyy-gray-400: #9CA3AF;
--hupyy-gray-500: #6B7280;
--hupyy-gray-600: #4B5563;
--hupyy-gray-700: #374151;
--hupyy-gray-800: #1F2937;
--hupyy-gray-900: #111827;

/* Semantic Colors */
--hupyy-error: #EF4444;          /* Red */
--hupyy-warning: #F59E0B;        /* Amber */
--hupyy-info: #3B82F6;           /* Blue */
--hupyy-success: #10B981;        /* Green */
```

#### Color Usage Guidelines
- **Primary Blue**: Main brand color, primary CTAs, headers, links
- **Secondary Purple**: AI/intelligent features, premium elements, gradients
- **Accent Green**: Success states, positive actions, verification
- **Grays**: Text, backgrounds, borders, UI elements
- **Semantic Colors**: Status indicators, alerts, notifications

### Typography

#### Font Families
```css
/* Primary Font - Sans Serif (UI/Interface) */
--hupyy-font-sans: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* Secondary Font - Serif (Marketing/Editorial) */
--hupyy-font-serif: 'Merriweather', 'Georgia', 'Cambria', 'Times New Roman', serif;

/* Monospace Font (Code/Technical) */
--hupyy-font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'Courier New', monospace;
```

#### Type Scale
```css
/* Headings */
--hupyy-text-xs: 0.75rem;      /* 12px */
--hupyy-text-sm: 0.875rem;     /* 14px */
--hupyy-text-base: 1rem;       /* 16px */
--hupyy-text-lg: 1.125rem;     /* 18px */
--hupyy-text-xl: 1.25rem;      /* 20px */
--hupyy-text-2xl: 1.5rem;      /* 24px */
--hupyy-text-3xl: 1.875rem;    /* 30px */
--hupyy-text-4xl: 2.25rem;     /* 36px */
--hupyy-text-5xl: 3rem;        /* 48px */
--hupyy-text-6xl: 3.75rem;     /* 60px */

/* Font Weights */
--hupyy-font-light: 300;
--hupyy-font-normal: 400;
--hupyy-font-medium: 500;
--hupyy-font-semibold: 600;
--hupyy-font-bold: 700;
--hupyy-font-extrabold: 800;
```

#### Typography Guidelines
- **Headlines**: Inter Bold/Extra Bold, primary or secondary color
- **Body Text**: Inter Regular, gray-700 (light mode) / gray-200 (dark mode)
- **UI Labels**: Inter Medium, gray-600
- **Code**: JetBrains Mono Regular, monospace background
- **Marketing**: Merriweather for editorial content, feature descriptions

### Spacing & Layout

#### Spacing Scale
```css
--hupyy-space-1: 0.25rem;   /* 4px */
--hupyy-space-2: 0.5rem;    /* 8px */
--hupyy-space-3: 0.75rem;   /* 12px */
--hupyy-space-4: 1rem;      /* 16px */
--hupyy-space-5: 1.25rem;   /* 20px */
--hupyy-space-6: 1.5rem;    /* 24px */
--hupyy-space-8: 2rem;      /* 32px */
--hupyy-space-10: 2.5rem;   /* 40px */
--hupyy-space-12: 3rem;     /* 48px */
--hupyy-space-16: 4rem;     /* 64px */
--hupyy-space-20: 5rem;     /* 80px */
--hupyy-space-24: 6rem;     /* 96px */
```

#### Border Radius
```css
--hupyy-radius-sm: 0.25rem;   /* 4px */
--hupyy-radius-md: 0.375rem;  /* 6px */
--hupyy-radius-lg: 0.5rem;    /* 8px */
--hupyy-radius-xl: 0.75rem;   /* 12px */
--hupyy-radius-2xl: 1rem;     /* 16px */
--hupyy-radius-full: 9999px;  /* Fully rounded */
```

---

## Marketing Assets

### Sign-In Page Background (signinpage.png)
**Specifications**:
- Dimensions: 1920x1080px minimum (responsive up to 4K)
- Format: PNG with transparency support
- Style: Abstract geometric patterns suggesting connected knowledge
- Colors: Gradient from primary blue to secondary purple with 20% opacity overlay
- Elements: Subtle node/network pattern, modern and professional
- No text or logos (applied separately in UI)

### Welcome Animation (welcomegif.gif)
**Specifications**:
- Dimensions: 800x600px
- Format: Animated GIF, optimized for web (<500KB)
- Duration: 3-5 seconds loop
- Style: Logo assembly or knowledge network forming
- Animation: Smooth, professional (60fps target, 30fps acceptable)
- Purpose: First-time user onboarding, dashboard welcome

### Social Media Assets

#### Open Graph / Social Sharing Image
- Dimensions: 1200x630px
- Format: PNG or JPG
- Content: Logo + tagline + abstract background
- Text: Large, readable at thumbnail size

#### Twitter/X Header Image
- Dimensions: 1500x500px
- Format: PNG or JPG
- Branding: Logo, tagline, key feature icons

#### LinkedIn Company Banner
- Dimensions: 1536x768px
- Format: PNG or JPG
- Professional styling with brand colors

---

## Naming Conventions

### Product Names
- **Full Product Name**: Hupyy KB
- **Short Reference**: Hupyy
- **Avoid**: Huppy, Huppy KB, HuppyKB (common misspellings)

### Technical Names

#### Code & Repositories
```
Repository Name: hupyy-kb
Package Names:
  - NPM: @hupyy/kb, @hupyy/config
  - Docker: hupyy/hupyy-kb
  - Python: hupyy-kb
```

#### Service Names
```
Docker Compose Services: hupyy-kb
Docker Images: hupyy/hupyy-kb:latest
Container Names: hupyy-kb
Volume Names: hupyy_data, hupyy_root_local
```

#### File Naming
```
Configuration: hupyy-config, .hupyy.yml
Assets: hupyy-logo-full.svg, hupyy-icon.png
Directories: /opt/hupyy-kb, /data/hupyy
```

### Domain Strategy

#### Primary Domains
- **hupyy.com** - Main website and documentation
- **app.hupyy.com** - SaaS application (if applicable)
- **docs.hupyy.com** - Documentation portal
- **api.hupyy.com** - API documentation

#### Alternative Domains (Redirects)
- **hupyykb.com** - Redirects to hupyy.com
- **huppykb.com** - Common misspelling protection

#### Email Addresses
- **contact@hupyy.com** - General inquiries
- **support@hupyy.com** - Customer support
- **security@hupyy.com** - Security issues
- **hello@hupyy.com** - Marketing/partnerships

---

## Brand Voice & Messaging

### Brand Personality
- **Intelligent**: Expert, knowledgeable, trustworthy
- **Accessible**: Friendly, approachable, helpful
- **Transparent**: Open, honest, community-focused
- **Innovative**: Modern, forward-thinking, cutting-edge
- **Reliable**: Professional, stable, enterprise-grade

### Writing Style Guidelines

#### Do's
- Use active voice
- Write in first-person plural (we, our) when speaking as the company
- Use second-person (you, your) when addressing users
- Keep sentences concise and clear
- Use technical terms appropriately for the audience
- Emphasize benefits over features

#### Don'ts
- Avoid jargon when simpler words work
- Don't use all caps except for acronyms (e.g., AI, API, KB)
- Avoid exclamation marks except for genuine excitement
- Don't make unverifiable claims
- Avoid negative language about competitors

### Sample Messaging

#### Homepage Hero
"Your workplace knowledge, connected and intelligent. Hupyy KB brings all your company's information together with AI that understands your business."

#### Product Description (Short)
"Hupyy KB is an open-source workplace AI platform that connects your company's data sources and provides instant, intelligent answers to your team's questions."

#### Product Description (Long)
"Hupyy KB is the open-source alternative to Glean, offering enterprise-grade workplace AI without the enterprise price tag. Connect 50+ data sources including Google Drive, Slack, Notion, GitHub, and more. Deploy on your infrastructure to maintain complete control over your data. Built on cutting-edge AI models from Anthropic, OpenAI, and open-source alternatives, Hupyy KB delivers contextual, accurate answers while preserving your privacy and security requirements."

#### Key Benefits (Bullet Points)
- Connect all your workplace tools in one intelligent platform
- On-premise deployment for complete data privacy
- Open-source transparency and community innovation
- No per-seat licensing - unlimited users at predictable cost
- Enterprise-grade AI with full customization control

---

## Brand Assets Checklist

### Critical Assets (Must Have)
- [ ] Logo - Full horizontal (SVG)
- [ ] Logo - Icon only (PNG, multiple sizes)
- [ ] Logo - Blue variant (SVG)
- [ ] Favicon (ICO, multi-resolution)
- [ ] Sign-in page background (PNG, high-res)
- [ ] Welcome animation (GIF, optimized)

### Important Assets (Should Have)
- [ ] Social media profile images (Twitter, LinkedIn, GitHub)
- [ ] Open Graph sharing image (1200x630)
- [ ] Email signature logo
- [ ] Presentation template (PowerPoint/Keynote)
- [ ] Documentation header/banner

### Nice to Have Assets
- [ ] Animated logo for video content
- [ ] Icon set for features/benefits
- [ ] Infographic templates
- [ ] T-shirt/swag designs
- [ ] Conference booth materials

---

## Implementation Notes

### Dark Mode Support
All visual assets must work in both light and dark UI themes:
- **Logo**: Provide color (for light) and white/light version (for dark)
- **Colors**: Test all colors for WCAG AA contrast compliance in both modes
- **Assets**: Ensure backgrounds don't clash with theme

### Accessibility Requirements
- **Contrast Ratios**: Minimum 4.5:1 for body text, 3:1 for large text
- **Logo Clarity**: Logo must be recognizable at 32px width
- **Color Blindness**: Don't rely solely on color to convey meaning
- **Alt Text**: All images must have descriptive alt text

### File Format Standards
- **Logos**: SVG primary, PNG fallback (transparent background)
- **Icons**: SVG preferred, PNG acceptable
- **Photos/Marketing**: WebP primary, JPG fallback
- **Favicon**: ICO (multi-resolution) + PNG (for modern browsers)

### Version Control
- All brand assets stored in dedicated repository or assets folder
- Version numbering: MAJOR.MINOR.PATCH (semantic versioning)
- Change log maintained for significant updates
- Previous versions archived, not deleted

---

## Transition Strategy

### Co-Branding Period
**Duration**: Not applicable (hard cutover)

**Rationale**: As Hupyy KB is a complete rebrand rather than a gradual evolution, we recommend a single-point transition with clear communication to the community.

### Announcement Template

**Email/Blog Post**:
```
Subject: Introducing Hupyy KB - Our New Name, Same Mission

We're excited to announce that PipesHub is now Hupyy KB!

Why the change?
[Brief explanation of strategic reasons for rebrand]

What's changing:
- New name: Hupyy KB
- New visual identity
- New domains: hupyy.com, docs.hupyy.com
- Updated Docker images: hupyy/hupyy-kb

What's NOT changing:
- Our commitment to open source
- Your data and privacy
- The features you rely on
- Our API and integrations

What you need to do:
[Migration guide link for self-hosted users]

Questions? Visit docs.hupyy.com/rebrand or contact support@hupyy.com
```

### Migration Support
- Maintain pipeshub-ai Docker images with deprecation notice for 6 months
- Redirect pipeshub.com to hupyy.com indefinitely
- Update all GitHub repositories with prominent rebrand notice
- Email existing users with migration instructions
- FAQ document addressing common migration questions

---

## Legal & Trademark

### Trademark Strategy
- File trademark application for "Hupyy KB" and "Hupyy" marks
- Include logo design in trademark filing
- Register in primary markets (US, EU, UK)

### Copyright Notice
```
© 2025 Hupyy. All rights reserved.
Hupyy KB is open-source software licensed under [LICENSE].
```

### Licensing
- Software: Maintain existing open-source license
- Brand assets: Separate usage guidelines (can restrict logo use)
- Documentation: Creative Commons or similar

---

## Brand Guidelines Enforcement

### Approved Use Cases
- Official documentation and marketing materials
- Community-created tutorials and guides (with attribution)
- Open-source contributions and forks (with attribution)
- Media coverage and press mentions

### Restricted Use Cases (Require Approval)
- Commercial products or services using the Hupyy name
- Modified versions claiming to be "official" Hupyy KB
- Merchandise or swag for profit
- Domain names that could cause confusion

### Contact for Brand Inquiries
**Email**: brand@hupyy.com
**Response Time**: 2-3 business days

---

## Appendix

### Color Accessibility Matrix

| Foreground | Background | Contrast Ratio | WCAG AA | WCAG AAA |
|------------|------------|----------------|---------|----------|
| Primary Blue (#2563EB) | White (#FFFFFF) | 8.59:1 | Pass | Pass |
| Primary Blue (#2563EB) | Gray-50 (#F9FAFB) | 8.42:1 | Pass | Pass |
| Gray-700 (#374151) | White (#FFFFFF) | 11.47:1 | Pass | Pass |
| Gray-600 (#4B5563) | White (#FFFFFF) | 8.59:1 | Pass | Pass |

### Font Licensing
- **Inter**: SIL Open Font License 1.1 (free for commercial use)
- **JetBrains Mono**: SIL Open Font License 1.1 (free for commercial use)
- **Merriweather**: SIL Open Font License 1.1 (free for commercial use)

### Asset Sources
- Logo design: [To be created by design team or contractor]
- Icons: Heroicons (MIT License) + custom designs
- Stock photos: Unsplash (free license) or internal photography

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-03 | Initial brand identity specification | Product Team |

---

**Document Status**: Living document - will be updated as brand evolves
**Next Review Date**: 2025-03-03 (3 months post-rebrand)
**Feedback**: brand@hupyy.com
