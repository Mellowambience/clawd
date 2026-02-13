# moltbot - Mobile App Design Document

## Design Philosophy

moltbot is a personal AI assistant for iOS that brings the power of OpenClaw to mobile devices. The design follows **Apple Human Interface Guidelines (HIG)** to feel like a native iOS app with intuitive one-handed usage in portrait orientation (9:16).

## Screen List

### 1. Chat Screen (Home/Primary)
**Primary Content:**
- Conversational chat interface with AI assistant
- Message bubbles (user messages on right, AI responses on left)
- Text input field at bottom with send button
- Chat history scrolls vertically

**Functionality:**
- Send text messages to AI
- View AI responses in real-time
- Scroll through conversation history
- Quick action buttons for common tasks

### 2. Tasks Screen
**Primary Content:**
- List of active tasks and reminders
- Task cards showing title, due date, status
- Quick add button for new tasks
- Filter/sort options (all, today, upcoming, completed)

**Functionality:**
- View all tasks created through AI conversations
- Mark tasks as complete
- Edit or delete tasks
- Create new tasks manually

### 3. Integrations Screen
**Primary Content:**
- Grid/list of available service integrations
- Integration cards showing service name, icon, connection status
- Categories: Productivity, Communication, Smart Home, Health

**Functionality:**
- Connect/disconnect services
- View integration status
- Configure integration settings
- Browse available integrations

### 4. Profile Screen
**Primary Content:**
- User profile information
- App settings and preferences
- AI model selection
- Theme toggle (light/dark)
- About and help sections

**Functionality:**
- Edit user profile
- Configure AI settings
- Manage app preferences
- View app information
- Access help/support

## Key User Flows

### Flow 1: Chat with AI Assistant
1. User opens app → lands on Chat Screen
2. User types message in input field
3. User taps send button
4. AI processes request and responds
5. Response appears in chat with typing indicator
6. User can continue conversation

### Flow 2: Create Task via AI
1. User asks AI to "remind me to call John at 3pm"
2. AI confirms task creation
3. Task appears in Tasks Screen
4. User receives notification at scheduled time

### Flow 3: Connect Service Integration
1. User navigates to Integrations Screen
2. User taps on service card (e.g., Calendar)
3. Integration sheet appears with connection options
4. User authorizes connection
5. Integration status updates to "Connected"
6. AI can now access that service

### Flow 4: Customize Settings
1. User navigates to Profile Screen
2. User taps on Settings section
3. User adjusts preferences (AI model, theme, notifications)
4. Changes save automatically
5. User returns to main screen

## Color Choices

**Brand Colors:**
- **Primary**: `#FF6B35` (Vibrant Orange) - Energetic, friendly, approachable AI assistant
- **Secondary**: `#004E89` (Deep Blue) - Trust, intelligence, reliability
- **Accent**: `#00A896` (Teal) - Modern, tech-forward, calming

**UI Colors:**
- **Background (Light)**: `#FFFFFF` (White)
- **Background (Dark)**: `#1A1A1A` (Near Black)
- **Surface (Light)**: `#F7F7F7` (Light Gray)
- **Surface (Dark)**: `#2A2A2A` (Dark Gray)
- **Text (Light)**: `#1A1A1A` (Near Black)
- **Text (Dark)**: `#FFFFFF` (White)
- **Muted (Light)**: `#6B7280` (Gray)
- **Muted (Dark)**: `#9CA3AF` (Light Gray)
- **Border (Light)**: `#E5E7EB` (Light Border)
- **Border (Dark)**: `#374151` (Dark Border)

## Design Patterns

### Navigation
- **Tab Bar Navigation** at bottom with 4 tabs:
  - Chat (house icon)
  - Tasks (checklist icon)
  - Integrations (grid icon)
  - Profile (person icon)

### Typography
- **Headings**: SF Pro Display (iOS system font), Bold, 24-28pt
- **Body**: SF Pro Text, Regular, 16pt
- **Captions**: SF Pro Text, Regular, 14pt

### Spacing
- **Screen padding**: 16px
- **Card padding**: 16px
- **Element spacing**: 8-12px
- **Section spacing**: 24px

### Components
- **Cards**: Rounded corners (12px), subtle shadow, white/dark background
- **Buttons**: Rounded (8px), primary color, haptic feedback
- **Input fields**: Rounded (8px), border, clear button
- **Message bubbles**: Rounded (16px), different colors for user/AI

### Interactions
- **Tap feedback**: Opacity change + haptic feedback
- **Loading states**: Skeleton screens or spinners
- **Animations**: Subtle, 200-300ms duration
- **Gestures**: Swipe to delete, pull to refresh

## iOS-Specific Considerations

- Safe area insets for notch and home indicator
- Native keyboard handling with proper dismiss behavior
- iOS-style navigation and transitions
- System font (SF Pro) for native feel
- Haptic feedback for interactions
- Dark mode support with automatic switching
- Accessibility support (VoiceOver, Dynamic Type)

## No Backend Requirements

This is a **local-first app** - no user authentication or cloud storage unless explicitly requested. All data stored locally using AsyncStorage for privacy and simplicity.
