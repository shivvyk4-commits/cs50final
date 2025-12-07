# Lango - Spanish Learning Platform Design Guidelines

## Design Approach

**Reference-Based Approach**: Drawing inspiration from successful learning platforms like Duolingo, Memrise, and Linear's clean interface aesthetics. Focus on creating an approachable, progress-driven experience that makes language learning feel achievable and engaging.

## Core Design Principles

1. **Progressive Clarity**: Each step in the learning journey should be visually distinct and feel like forward progress
2. **Friendly Professionalism**: Warm and approachable without being childish
3. **Focus-Driven Layouts**: Minimize distractions during learning activities
4. **Clear Hierarchy**: Always make the next action obvious

## Typography

**Font Families** (Google Fonts):
- Primary: Inter (UI elements, body text)
- Accent: Bricolage Grotesque or Space Grotesk (headings, lesson titles)

**Type Scale**:
- Hero/Landing: 4xl to 6xl, bold
- Page Headers: 3xl, semibold
- Section Headers: 2xl, semibold
- Lesson Content: xl, medium
- Body Text: base, regular
- UI Labels: sm, medium
- Captions: xs, regular

## Layout System

**Spacing Primitives**: Use Tailwind units of 2, 4, 6, 8, 12, 16, 20, and 24
- Component padding: p-4 to p-6
- Section spacing: py-12 to py-20
- Card spacing: p-6 to p-8
- Element gaps: gap-4 to gap-8

**Container Strategy**:
- Marketing pages: max-w-7xl
- App dashboard: max-w-6xl
- Lesson content: max-w-3xl
- Chat interface: max-w-2xl

## Component Library

### Navigation
**Landing Page Header**:
- Clean, transparent-to-solid on scroll
- Logo left, navigation center, CTA right
- Include "Get Started" primary button

**App Dashboard Navigation**:
- Persistent left sidebar (w-64) with:
  - User profile summary at top
  - Navigation links (Dashboard, Lessons, Schedule, Progress)
  - Calendar sync status indicator
- Collapsible on mobile (hamburger menu)

### Landing Page Sections

**Hero Section** (80vh):
- Large hero image showing diverse people learning/conversing
- Centered content overlay with blurred background panels for text/buttons
- Headline emphasizing "Learn Spanish Through Conversation"
- Primary CTA: "Start Learning Free"
- Secondary element: Trust indicators ("Join 10,000+ learners")

**How It Works** (3-column grid on desktop):
- Icon + Title + Description cards
- Steps: "Set Your Schedule" → "Learn Vocabulary" → "Practice Conversations"
- Use simple, modern icons (Heroicons)

**Features Showcase** (alternating 2-column layouts):
- Row 1: Image left, text right - Smart Scheduling
- Row 2: Text left, image right - AI Conversations
- Row 3: Image left, text right - Track Progress
- Each section py-20 with generous whitespace

**Social Proof**:
- 3-column testimonial cards with student photos
- Include name, experience level, and quote

**CTA Section**:
- Centered, py-24
- Bold headline, supporting text
- Primary button + "No credit card required" subtext

**Footer**:
- 3-column layout: About/Links, Resources, Contact
- Newsletter signup integrated
- Social media links

### Registration & Onboarding

**Multi-step Form**:
- Progress indicator at top (Step 1 of 3)
- Step 1: Email/Password + Name
- Step 2: Experience level (slider 0-10 years) + Lesson duration (15/30/45/60 min radio buttons)
- Step 3: Calendar integration with "Connect Google Calendar" button or manual time selection
- Use large, touch-friendly inputs (h-12)
- Clear validation states

### Dashboard

**Layout Structure**:
- Welcome header with user name and current streak
- 2-column grid:
  - Left: "Today's Lesson" card (larger, featured)
  - Right: "Upcoming Schedule" mini calendar + "Your Progress" stats
- Below: "Continue Learning" path showing lesson categories as clickable cards

**Lesson Category Cards**:
- Grid layout (2-3 columns)
- Each card: Icon, category name (Food, Clothing, Greetings, etc.), progress bar, lesson count
- Distinct visual state for locked/unlocked/completed

### Lesson Interface

**Vocabulary Section**:
- Flashcard-style presentation
- Large Spanish word (3xl, bold)
- English translation below (xl, regular)
- Pronunciation guide (text-sm, muted)
- Navigation: Previous/Next buttons at bottom
- Progress bar at top showing position in set

**Verb Conjugation Section**:
- Table layout showing conjugations
- Highlight pattern differences
- Example sentences using each form
- Interactive quiz mode: fill-in-the-blank style

### AI Chatbot Conversation

**Chat Interface** (max-w-2xl, centered):
- Fixed header: Lesson topic + Exit button
- Scrollable message area (min-h-96)
- Message bubbles:
  - AI messages: left-aligned, soft gray background
  - User messages: right-aligned, accent color background
- Fixed input area at bottom:
  - Large textarea (min-h-24)
  - Character count indicator
  - "Send" button (disabled until text entered)
- Typing indicator when AI is responding

**Prompt Examples** (displayed initially):
- Show 2-3 sample prompts user can click
- Example: "Tell me about your favorite food" or "Describe your typical day"

### Calendar Integration

**Schedule Picker**:
- Weekly calendar view showing available/blocked times
- Visual indicators for already-scheduled lessons
- Time slot selection (30-minute increments)
- Confirmation modal showing lesson details before calendar add

### Progress Tracking

**Stats Dashboard**:
- Grid of metric cards (2-3 columns):
  - Current streak (days)
  - Total lessons completed
  - Vocabulary words learned
  - Conversation hours
- Line chart showing progress over time
- Category breakdown (pie chart or bar chart)

## Interaction Patterns

- **Hover states**: Subtle lift (translate-y-1) + shadow increase
- **Focus states**: Clear outline (ring-2) in accent color
- **Loading states**: Minimal spinner, never block entire screen
- **Success feedback**: Green checkmark animation, brief confirmation message
- **Error states**: Inline, red text with icon, specific guidance

## Accessibility

- Minimum touch target: 44x44px
- Color contrast: WCAG AA minimum (4.5:1 for text)
- Skip navigation links
- ARIA labels for all interactive elements
- Keyboard navigation support throughout

## Images

**Hero Image**: 
- Wide landscape showing people in conversation/learning setting
- Warm, inviting lighting
- Diverse representation
- Subtle overlay for text legibility

**Feature Images**:
- Screenshot mockups of calendar integration
- Chat interface examples
- Progress dashboard views
- Use subtle shadows/borders for depth

**Testimonial Photos**:
- Authentic headshots, circular crop
- Consistent sizing (w-16 h-16)

This design creates a professional, encouraging learning environment that feels modern while keeping users focused on their language learning goals.