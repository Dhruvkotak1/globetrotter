# 🌍 GlobeTrotter — Empowering Personalized Travel Planning

GlobeTrotter is a full-stack, responsive multi-city travel planning web application built with **Flask**, **SQLAlchemy**, and **Chart.js**. It empowers travelers to dream, design, and organize personalized itineraries, estimate budgets, navigate timelines and calendars, and discover shared itineraries from a global community.

---

## ✨ Features & Screens (13/13 Mapped)

1. **Login & Registration**: Secure authentication, profile management, and token-based password resets.
2. **Dashboard / Home Screen**: Hero exploration banner, fast search, popular destinations, and recent trips.
3. **Plan a New Trip**: Multi-day trip creation wizard with date pickers, target budget, and cover photos.
4. **My Trips Hub**: Filter trips by **Ongoing**, **Upcoming**, and **Completed** with instant search & sort.
5. **Itinerary Builder**: Multi-stop city manager with dynamic activity assignments and live cost summaries.
6. **Day-wise Itinerary & Timeline**: Expandable day accordions with physical activities and daily expenditure breakdown.
7. **City Search & Directory**: Search global cities with cost indices, popularity scores, and 1-click "Add to Trip".
8. **Activity Search**: Filter experiences by category, max cost, and duration, with quick-add to stops.
9. **Budget & Cost Analytics**: Interactive Chart.js Donut & Bar charts, overbudget alerts, and custom expense receipts.
10. **Trip Visual Calendar**: Interactive monthly calendar with active date ranges and activity event markers.
11. **Shared / Community Hub**: Public gallery of verified travel plans with a **1-click "Copy Trip"** cloner.
12. **User Profile & Settings**: Preplanned trips, past travel history, destination wishlist, and account settings.
13. **Admin Analytics Dashboard**: Role-gated overview of platform adoption, trip trends, and user moderation.

---

## 🗄️ Tech Stack & Database

- **Backend**: Python 3, Flask (Application Factory & Blueprints)
- **Database**: SQLite / SQLAlchemy ORM (`Flask-SQLAlchemy`) — easily switchable to PostgreSQL/MySQL via `DATABASE_URL` in `config.py`
- **Authentication**: Flask-Login & Werkzeug security hashing
- **Frontend**: Responsive HTML5, CSS3 Glassmorphism, Vanilla JS, Chart.js, FontAwesome 6

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Populate Database with Demo Data
```bash
python seed_data.py
```

### 3. Run the Application
```bash
python run.py
```
Open **`http://localhost:5000`** in your browser.

---

## 🔑 Demo Test Accounts

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@globetrotter.com` | `admin123` |
| **Traveler** | `traveler@globetrotter.com` | `travel123` |
| **Community Creator** | `sarah@globetrotter.com` | `explore123` |

---

## 🧪 Run Automated Tests

```bash
python test_app.py
```
