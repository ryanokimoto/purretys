# Purretys - Complete Project Roadmap

## 🎯 Project Vision & Goals

**Core Concept**: Create a collaborative virtual pet care game where multiple users can share responsibility for raising the same cat, completing real-life tasks to earn currency and improve their pet's wellbeing.

**Target Users**: Friends, families, roommates, study groups, and teams who want to gamify their daily goals while bonding over a shared virtual pet.

## 📋 Complete Project Roadmap

### Phase 1: Foundation
**Goal**: Set up core infrastructure and basic functionality

#### 1.1 Project Setup
- [X] Initialize Git repository with proper .gitignore
- [X] Set up monorepo structure (backend/frontend/shared)
- [X] Create documentation templates
- [ ] Set up development environment configs
- [ ] Configure ESLint, Prettier, and TypeScript configs
- [ ] Configure Docker Containers

#### 1.2 Basic Backend
- [ ] FastAPI application skeleton
- [ ] Database models:
  ```python
  # Core models
  - User (id, email, username, avatar)
  - Pet (id, name, created_at)
  - PetOwnership (user_id, pet_id, role, joined_at)
  - PetMetrics (pet_id, happiness, hunger, health, energy, currency)
  - Task (id, pet_id, title, difficulty, reward, created_by)
  - TaskCompletion (task_id, user_id, completed_at)
  ```
- [ ] JWT authentication system
- [ ] WebSocket setup for real-time updates
- [ ] Basic API endpoints (register, login, create_pet)

#### 1.3 Basic Frontend
- [ ] React + TypeScript setup with Vite
- [ ] Basic routing (login, register, pet dashboard, tasks)
- [ ] Authentication flow with protected routes
- [ ] Zustand/Redux for state management
- [ ] TailwindCSS + shadcn/ui setup
- [ ] Responsive mobile-first design

### Phase 2: Core Pet Mechanics
**Goal**: Implement the virtual pet system

#### 2.1 Pet Creation & Display
- [ ] Pet creation flow (name, appearance customization)
- [ ] Pet sprite/avatar system
- [ ] Basic animations (idle, happy, sad, sleeping)
- [ ] Pet profile page
- [ ] Invite system for co-owners

#### 2.2 Metrics System
```typescript
interface PetMetrics {
  happiness: number;  // 0-100
  hunger: number;     // 0-100
  health: number;     // 0-100
  energy: number;     // 0-100
  currency: number;   // shared wallet
}
```
- [ ] Real-time metric updates
- [ ] Metric decay system (configurable rates)
- [ ] Visual indicators (progress bars, icons)
- [ ] Alert system for critical levels
- [ ] Metric history tracking

#### 2.3 Currency System
- [ногоShared wallet implementation
- [ ] Transaction history
- [ ] Currency earning from tasks
- [ ] Spending tracking
- [ ] Balance display for all co-owners

### Phase 3: Care & Interaction
**Goal**: Build pet care features

#### 3.1 Feeding System
- [ ] Food inventory database
- [ ] Catnip item (initial food)
- [ ] Purchase interface
- [ ] Feeding animation
- [ ] Food effects on metrics:
  ```python
  # Food effects
  catnip: {
    "happiness": +20,
    "hunger": -30,
    "energy": +10,
    "cost": 10
  }
  ```
- [ ] Feeding cooldown system

#### 3.2 Mini-Games
- [ ] Pet the Cat mini-game:
  - [ ] Touch/click interaction
  - [ ] Happiness boost mechanics
  - [ ] Petting animations
  - [ ] Daily interaction limits
- [ ] Score tracking
- [ ] Rewards for mini-game completion

#### 3.3 Pet States
- [ ] Dynamic pet mood based on metrics
- [ ] Visual feedback (expressions, sounds)
- [ ] Special animations for different states
- [ ] Sleep cycle (energy regeneration)

### Phase 4: Task System
**Goal**: Implement real-world task integration

#### 4.1 Task Creation
- [ ] Task builder interface
- [ ] Task categories:
  ```typescript
  enum TaskCategory {
    EXERCISE = "exercise",
    HYDRATION = "hydration", 
    STUDY = "study",
    CHORES = "chores",
    SOCIAL = "social",
    CUSTOM = "custom"
  }
  ```
- [ ] Difficulty levels (Easy: 5 coins, Medium: 10 coins, Hard: 20 coins)
- [ ] Recurring task options (daily, weekly)
- [ ] Task assignment to specific users

#### 4.2 Task Management
- [ ] Task list view (personal & shared)
- [ ] Task completion flow
- [ ] Proof/verification system (photo, timer, honor system)
- [ ] Task history
- [ ] Streak tracking

#### 4.3 Rewards & Metrics Impact
- [ ] Currency distribution on completion
- [ ] Metric boost system:
  ```python
  task_metric_mapping = {
    "exercise": {"health": +10, "energy": +5},
    "hydration": {"health": +5},
    "study": {"happiness": +5},
  }
  ```
- [ ] Achievement system
- [ ] Leaderboard among co-owners

### Phase 5: Collaboration Features
**Goal**: Enable seamless multi-user interaction

#### 5.1 Real-time Synchronization
- [ ] WebSocket implementation for live updates
- [ ] Presence system (who's online)
- [ ] Activity feed (who fed the pet, completed tasks)
- [ ] Push notifications for critical events

#### 5.2 Communication
- [ ] In-app messaging between co-owners
- [ ] Pet care notes/journal
- [ ] Task comments
- [ ] @mentions in messages

#### 5.3 Permissions & Roles
- [ ] Owner vs co-owner permissions
- [ ] Invite management
- [ ] Remove user functionality
- [ ] Pet transfer ownership

### Phase 6: Mobile App Development
**Goal**: Create native mobile experience

#### 6.1 Mobile Foundation
- [ ] React Native setup
- [ ] Shared component library
- [ ] API integration layer
- [ ] Authentication flow

#### 6.2 Mobile-Specific Features
- [ ] Push notifications
- [ ] Device reminders for tasks
- [ ] Camera integration for task proof
- [ ] Offline mode with sync
- [ ] Haptic feedback for interactions

#### 6.3 App Store Deployment
- [ ] iOS build and testing
- [ ] Android build and testing
- [ ] App store listings
- [ ] Beta testing program

### Phase 7: Enhanced Features
**Goal**: Add depth and engagement

#### 7.1 Expanded Pet Care
- [ ] Multiple food types with different effects
- [ ] Toys and accessories shop
- [ ] Pet customization (colors, accessories)
- [ ] Pet evolution/growth stages
- [ ] Special events (birthdays, holidays)

#### 7.2 Advanced Mini-Games
- [ ] Catch the Mouse game
- [ ] Laser Pointer Chase
- [ ] Memory Match with cat themes
- [ ] Puzzle solving for bonus rewards
- [ ] Daily challenges

#### 7.3 Social Features
- [ ] Pet visits between friends
- [ ] Pet playdates
- [ ] Global leaderboard
- [ ] Pet showcases
- [ ] Community challenges

### Phase 8: Gamification & Progress
**Goal**: Long-term engagement mechanics

#### 8.1 Achievement System
- [ ] Achievement categories
- [ ] Badges and trophies
- [ ] Milestone rewards
- [ ] Collection displays
- [ ] Rare achievements

#### 8.2 Progression System
- [ ] Pet levels based on care quality
- [ ] Unlock new items/features with levels
- [ ] Seasonal content
- [ ] Special event pets
- [ ] Prestige system

#### 8.3 Analytics & Insights
- [ ] Personal habit tracking
- [ ] Task completion trends
- [ ] Pet care statistics
- [ ] Group performance metrics
- [ ] Weekly/monthly reports

## 🏗️ Technical Architecture Decisions

### Backend Architecture
```
API Layer (FastAPI)
    ↓
WebSocket Layer (Real-time updates)
    ↓
Service Layer (Game Logic, Task Management)
    ↓
Data Layer (PostgreSQL + Redis for caching)
    ↓
Background Tasks (Celery for metric decay, notifications)
```

### Key Technology Choices
1. **Database**: PostgreSQL for relational data, Redis for caching/sessions
2. **Real-time**: WebSockets via FastAPI for live updates
3. **Authentication**: JWT with refresh tokens
4. **Task Queue**: Celery + Redis for background jobs
5. **Mobile**: React Native for cross-platform mobile app
6. **State Management**: Zustand for React, Redux Toolkit for React Native

### Database Schema (Core Tables)
```sql
-- Users and Authentication
users (id, email, username, avatar_url, created_at)
sessions (id, user_id, token, expires_at)

-- Pet System
pets (id, name, sprite_id, created_at, created_by)
pet_ownership (id, pet_id, user_id, role, joined_at)
pet_metrics (id, pet_id, happiness, hunger, health, energy, currency, updated_at)
pet_metric_history (id, pet_id, metric_type, value, timestamp)

-- Tasks
tasks (id, pet_id, title, description, category, difficulty, reward, created_by, recurring_pattern)
task_completions (id, task_id, user_id, completed_at, proof_url)
task_assignments (id, task_id, user_id, assigned_at)

-- Items and Transactions
items (id, name, type, cost, effects_json)
inventory (id, pet_id, item_id, quantity)
transactions (id, pet_id, user_id, amount, type, description, created_at)

-- Social
messages (id, pet_id, user_id, content, created_at)
notifications (id, user_id, type, content, read, created_at)
```

## 📊 Success Metrics

1. **User Engagement**
   - Daily active users > 60%
   - Average session time > 5 minutes
   - Task completion rate > 70%
   - Multi-user pets > 40%

2. **Technical Performance**
   - API response time < 200ms
   - WebSocket latency < 100ms
   - 99.9% uptime
   - Support 10,000+ concurrent users

3. **Game Metrics**
   - Pet survival rate > 90%
   - Average pet age > 30 days
   - Tasks per user per day > 3
   - User retention (30 day) > 40%

## 🚀 MVP Definition

**Minimum Viable Product includes:**
1. User authentication (register/login)
2. Create and name a single cat
3. View and manage 4 core metrics
4. Invite one other user to co-own
5. Create and complete basic tasks
6. Earn and spend currency on catnip
7. Pet the cat mini-game
8. Real-time metric updates
9. Basic web interface (mobile-responsive)

**MVP does NOT include:**
1. Mobile app
2. Multiple pets
3. Advanced mini-games
4. Pet customization
5. Achievements
6. Social features beyond co-ownership

## 💡 Development Tips

1. **Start with Single-Player**: Get core mechanics working before collaboration
2. **Focus on Core Loop**: Task → Currency → Care → Happiness
3. **Simple Graphics First**: Use CSS/SVG before complex sprites
4. **Test Multiplayer Early**: WebSocket sync can be tricky
5. **Balance Carefully**: Metric decay rates and rewards need tuning
6. **Mobile-First Design**: Most users will eventually use mobile

## 📚 Resources & References

### Technical Resources
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [React Native Setup](https://reactnative.dev/docs/environment-setup)
- [Zustand State Management](https://github.com/pmndrs/zustand)
- [Socket.io vs WebSockets](https://socket.io/docs/v4/)

### Game Development
- [Game Balance Concepts](https://www.gamedeveloper.com/design/the-fundamentals-of-game-balance)
- [Virtual Pet Mechanics](https://en.wikipedia.org/wiki/Digital_pet)
- [Gamification in Apps](https://www.interaction-design.org/literature/topics/gamification)

### Libraries & Tools
- **Backend**: fastapi, sqlalchemy, pydantic, celery, redis-py, python-jose[cryptography]
- **Frontend**: react, typescript, tailwind, shadcn/ui, zustand, framer-motion
- **Mobile**: react-native, expo, react-navigation
- **Real-time**: websockets, python-socketio (alternative)
- **Testing**: pytest, jest, react-testing-library
- **Deployment**: docker, nginx, postgresql, redis

## 🎯 Next Steps

1. **Week 1**: Set up development environment and basic authentication
2. **Week 2**: Create pet model and basic metrics system
3. **Week 3**: Implement task creation and completion
4. **Week 4**: Add currency system and catnip feeding
5. **Week 5**: Build pet mini-game and WebSocket updates
6. **Week 6**: Implement multi-user collaboration
7. **Week 7**: Testing and bug fixes
8. **Week 8**: Deploy MVP and gather feedback

## 🚧 Risk Mitigation

1. **Real-time Sync Issues**: Start with polling, upgrade to WebSockets
2. **Metric Balance**: Implement config-based rates for easy tuning
3. **User Retention**: Focus on daily tasks and streaks early
4. **Scaling**: Design database with sharding in mind
5. **Mobile Transition**: Keep web app mobile-first from start

---

*Version 1.0 - Focus on shipping a fun, working MVP that proves the collaborative pet care concept*