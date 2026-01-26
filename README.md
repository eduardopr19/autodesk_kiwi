# 🥝 AutoDesk Kiwi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A personal productivity hub that centralizes tasks, calendar, weather, and daily essentials in one elegant dark-themed interface.

---

## 🌟 Overview

**AutoDesk Kiwi** is a modern personal productivity dashboard designed to streamline your daily workflow. Built with a clean, dark-mode interface, it aggregates tasks, schedules, weather forecasts, and Hyperplanning integration into a single, responsive web application.

### Why Kiwi?

- **🎯 All-in-One Dashboard**: View your tasks, schedule, weather, and grades in a unified interface
- **🌙 Modern Dark UI**: Eye-friendly design with smooth animations and responsive layout
- **⚡ Fast & Lightweight**: No complex build process - pure HTML/CSS/JS with Alpine.js
- **🔒 Privacy-First**: Self-hosted with local SQLite database - your data stays with you
- **🎓 Student-Focused**: Native Hyperplanning integration for French students

---

## ✨ Features

### 📋 Task Management
- Create, update, and delete tasks with ease
- Priority levels: Low, Normal, High
- Status tracking: Todo, In Progress, Done
- Advanced filtering by status, priority, or search query
- Sorting by date, priority, or title
- Bulk deletion support

### 📅 Hyperplanning Integration
- **Schedule View**: Automatic iCalendar parsing from Hyperplanning
- **Next Courses**: Quick view of upcoming classes
- **Statistics**: Track hours per subject (done vs. planned)
- **Grades Import**: Manual import system for grades/notes (JSON format)
- Timezone-aware (Europe/Paris)

### 🌤️ Weather Integration
- Real-time weather via Open-Meteo API
- Hourly and daily forecasts
- Automatic geolocation with reverse geocoding (Nominatim)
- Weather code mapping with icons

### 🖥️ Personal Dashboard
- Quote of the day
- Next upcoming event
- Real-time weather widget
- Email summary (Proton, Outlook) - coming soon

### 🎨 Responsive Design
- Mobile-friendly interface
- Desktop optimized
- Dark mode only (optimized for night work)
- Smooth transitions and animations

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast async API
- **Database**: SQLite with [SQLModel](https://sqlmodel.tiangolo.com/) ORM
- **Validation**: Pydantic models with type hints
- **Logging**: Colored console logging
- **Middleware**: CORS, GZip compression, request timing

### Frontend
- **Framework**: [Alpine.js](https://alpinejs.dev/) - Lightweight reactive framework
- **Styling**: Vanilla CSS with CSS custom properties
- **Icons**: Emoji-based for simplicity
- **Storage**: LocalStorage for UI state persistence

### External APIs
- **Open-Meteo**: Weather data
- **Nominatim**: Reverse geocoding
- **Hyperplanning**: iCalendar schedule feed

---

## 📦 Installation

### Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kiwi6212/autodesk_kiwi.git
   cd autodesk_kiwi
   ```

2. **Navigate to the API directory**
   ```bash
   cd api
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv .venv

   # On Windows
   .venv\Scripts\activate

   # On macOS/Linux
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your values:
   ```env
   APP_NAME="AutoDesk Kiwi API"
   DEBUG=true
   DATABASE_URL="sqlite:///data.db"

   # Optional: Add your Hyperplanning iCal URL
   HYPERPLANNING_URL="https://your-hyperplanning-url-here"
   ```

6. **Start the backend server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://127.0.0.1:8000`
   - Interactive docs: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

7. **Open the frontend**
   - Simply open `web/index.html` in your browser
   - Or serve it with a local server:
     ```bash
     # Python simple server
     cd web
     python -m http.server 5500
     ```
   - Access at `http://localhost:5500`

---

## 🚀 Usage

### Adding Tasks
1. Navigate to the **Tasks** section
2. Click the **"+ Add Task"** button
3. Fill in title, description (optional), and priority
4. Tasks appear immediately in your list

### Filtering & Searching
- Use the search bar to find tasks by title
- Filter by status: `todo`, `in_progress`, `done`
- Filter by priority: `low`, `normal`, `high`
- Sort by date, priority, or title (ascending/descending)

### Importing Grades
1. Navigate to **Hyperplanning** → **Notes** section
2. Click **"➕ Importer"**
3. Paste JSON data in the format:
   ```json
   [
     {
       "subject": "Mathematics",
       "date": "13 Dec",
       "value": 18.5
     }
   ]
   ```
4. Click **"✅ Importer"** to save

> 💡 **Tip**: A sample `notes_import.json` file is included in the repository for reference.

### Viewing Weather
- Click **"📍 Allow location access"** on first load
- Weather automatically updates based on your location
- View hourly and daily forecasts

---

## 📂 Project Structure

```
autodesk_kiwi/
├── api/                          # Backend FastAPI application
│   ├── routes/                   # API endpoints
│   │   ├── tasks.py              # Task CRUD operations
│   │   ├── hyperplanning.py      # Hyperplanning integration
│   │   ├── integrations.py       # Weather & geocoding APIs
│   │   └── meta.py               # Health check & overview
│   ├── main.py                   # Application entry point
│   ├── models.py                 # Pydantic/SQLModel schemas
│   ├── db.py                     # Database session management
│   ├── config.py                 # Settings & configuration
│   ├── logger.py                 # Logging setup
│   ├── exceptions.py             # Custom exception handlers
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (not committed)
│   └── .env.example              # Environment template
├── web/                          # Frontend application
│   ├── index.html                # Main SPA file
│   ├── app.js                    # Alpine.js logic (337 lines)
│   ├── style.css                 # Dark theme styling (676 lines)
│   └── favicon.png               # App icon
├── docs/                         # Documentation
│   └── GRADES_IMPORT.md          # Grades import guide
├── .gitignore                    # Git ignore rules
├── LICENSE                       # MIT License
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── ROADMAP.md                    # Future plans
└── notes_import.json             # Sample grades for import
```

---

## 🗺️ Roadmap

### 🎯 **Priority Features (Next Up)**

These are the recommended improvements to implement first:

1. **🏷️ Tags/Labels System** - Organize tasks with colored tags
2. **🔍 Search & Advanced Filters** - Find tasks quickly with powerful search
3. **📱 PWA & Mobile Experience** - Use Kiwi as a mobile app with offline support

---

### 📋 **Task Management Enhancements**

- [ ] **Tags/Labels personnalisés**
  - Custom colored tags (work, personal, urgent, study, etc.)
  - Filter tasks by multiple tags
  - Tag statistics and insights

- [ ] **Search & Advanced Filters**
  - Full-text search across title and description
  - Multi-criteria filtering (date + priority + status + tags)
  - Save custom filter presets
  - Sort by multiple fields

- [ ] **Calendar View**
  - Monthly calendar visualization
  - Drag & drop to reschedule tasks
  - Week view with time blocks

- [ ] **Subtasks & Checklists**
  - Add checkable steps for each task
  - Progress tracking (3/5 completed)
  - Nested subtasks support

---

### 📊 **Analytics & Productivity**

- [x] **Productivity Statistics** ✅ (Implemented)
  - Charts for daily/weekly completion rates
  - Task distribution by status and priority

- [ ] **Streaks & Gamification**
  - Track consecutive days with completed tasks
  - Achievement badges and milestones
  - Productivity score calculation

- [ ] **Weekly Reports**
  - Automated email summary every Monday
  - Weekly productivity insights
  - Goal tracking and suggestions

- [ ] **Time Tracking**
  - Built-in timer for tasks
  - Time estimates vs actual time spent
  - Statistics per project/subject

---

### 🎨 **Interface & User Experience**

- [ ] **Dark Mode Automation**
  - Auto-switch based on time (day/night)
  - System theme detection
  - Custom schedule (e.g., dark mode 8pm-7am)

- [ ] **Keyboard Shortcuts**
  - `N` - New task
  - `S` - Focus search
  - `/` - Command palette
  - `Esc` - Close modals
  - Arrow keys for navigation

- [ ] **View Modes**
  - Compact list view (more items visible)
  - Card view (current)
  - Kanban board view

- [ ] **Customizable Dashboard**
  - Drag & drop widgets
  - Hide/show sections
  - Custom widget sizes

---

### 🔔 **Notifications & Reminders**

- [ ] **Task Reminders**
  - Browser desktop notifications
  - Configurable timing (15 min, 1 hour, 1 day before)
  - Recurring reminders for repeated tasks

- [ ] **Hyperplanning Alerts**
  - Notification 15 minutes before class
  - Daily summary of tomorrow's schedule
  - Changed course detection

- [ ] **Productivity Nudges**
  - "You haven't completed any tasks today"
  - "5 overdue tasks need attention"
  - Streak reminders

---

### 💾 **Import/Export Features**

- [x] **Grades Import (JSON)** ✅ (Implemented)

- [ ] **Task Export**
  - CSV format for Excel/Google Sheets
  - JSON format for backups
  - PDF report generation
  - iCal format for calendar apps

- [ ] **Import from Other Apps**
  - Trello board import
  - Todoist migration
  - Notion database sync
  - CSV/Excel import

- [ ] **Automatic Backups**
  - Daily database backups
  - Export to cloud storage (optional)
  - Version history (restore from backup)

---

### 🔗 **Integrations & API**

- [ ] **Complete REST API**
  - Full CRUD for all resources
  - Swagger/OpenAPI documentation
  - API authentication (JWT tokens)
  - Rate limiting

- [ ] **Webhooks**
  - Trigger actions on task completion
  - Integrate with Zapier/IFTTT
  - Custom automation workflows

- [ ] **Third-Party Integrations**
  - Google Calendar (read/write)
  - Microsoft Outlook sync
  - Slack notifications
  - Discord webhooks

---

### 📱 **Mobile & Offline**

- [ ] **Progressive Web App (PWA)**
  - Install as native app on mobile
  - Offline mode with service workers
  - Push notifications on mobile
  - App icon and splash screen

- [ ] **Responsive Improvements**
  - Better mobile navigation
  - Touch-optimized interactions
  - Swipe gestures (swipe to complete/delete)

- [ ] **Mobile-First Features**
  - Quick add widget
  - Voice input for tasks
  - Location-based reminders

---

### 🤖 **AI & Automation**

- [ ] **Smart Suggestions**
  - Detect patterns in task creation
  - Suggest recurrence rules
  - Auto-categorize tasks by content

- [ ] **Task Templates**
  - Reusable task templates
  - Project templates ("Morning Routine", "Weekly Review")
  - Template marketplace/sharing

- [ ] **Natural Language Input**
  - "Buy milk tomorrow at 3pm" → Parsed task
  - Smart date/time detection
  - Priority keywords ("urgent", "low priority")

---

### 🔐 **Security & Multi-User**

- [ ] **User Authentication**
  - JWT-based login system
  - Secure password hashing
  - Session management

- [ ] **Multi-User Support**
  - User accounts and profiles
  - Shared workspaces (optional)
  - Permission levels

- [ ] **Data Privacy**
  - End-to-end encryption option
  - GDPR compliance tools
  - Data export/deletion

---

### 🧪 **Developer Experience**

- [x] **Docker Support** ✅ (Implemented)
- [x] **Code Linting (Ruff)** ✅ (Implemented)
- [x] **Unit Tests** ✅ (Implemented)

- [ ] **CI/CD Pipeline**
  - GitHub Actions for testing
  - Automated deployment
  - Version tagging

- [ ] **Documentation**
  - API documentation improvements
  - Code comments and docstrings
  - Architecture diagrams

---

> 💡 **Want to contribute?** Pick any feature from this roadmap and open a PR!
> See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or code contributions.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit with clear messages (`git commit -m 'feat: add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Follow existing code style (PEP 8 for Python)
- Use type hints everywhere
- Write clear commit messages
- Add tests for new features
- Update documentation as needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tasks` | GET | List all tasks with filters |
| `/tasks` | POST | Create a new task |
| `/tasks/{id}` | PUT | Update a task |
| `/tasks/{id}` | DELETE | Delete a task |
| `/hyperplanning/courses` | GET | Get today's schedule |
| `/hyperplanning/grades` | GET | Get all grades |
| `/external/weather` | GET | Get current weather |
| `/external/forecast` | GET | Get weather forecast |

---

## 🔒 Security

- **Environment Variables**: Sensitive data stored in `.env` (not committed)
- **CORS**: Restricted to localhost during development
- **Input Validation**: Pydantic models validate all inputs
- **Error Handling**: Generic error messages to avoid information leakage

**Important**: Never commit your `.env` file or expose API tokens publicly.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Mathias Quillateau

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing async web framework
- [Alpine.js](https://alpinejs.dev/) - Lightweight reactivity
- [SQLModel](https://sqlmodel.tiangolo.com/) - Type-safe ORM
- [Open-Meteo](https://open-meteo.com/) - Free weather API
- [Nominatim](https://nominatim.org/) - OpenStreetMap geocoding

---

## 📧 Contact

**Mathias Quillateau**

- GitHub: [@Kiwi6212](https://github.com/Kiwi6212)
- Project Link: [https://github.com/Kiwi6212/autodesk_kiwi](https://github.com/Kiwi6212/autodesk_kiwi)

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ and ☕ by Mathias

</div>
