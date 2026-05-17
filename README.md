# SkillSwap

**A campus skill-exchange platform for university students.**

SkillSwap helps students discover skills offered by peers, post what they can teach, send exchange requests, and chat once connected — all in one place.

---

## Table of Contents

- [Overview](#overview)
- [Team Members](#team-members)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Running Tests](#running-tests)
- [Database & Migrations](#database--migrations)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

Many students have valuable skills — programming, design, languages, music, public speaking — but lack a simple way to find and connect with others on campus who want to learn or teach.

SkillSwap solves that by providing:

- A **browse & search** experience for skills posted by other students
- A **profile** to manage your details and the skills you offer
- A **request workflow** to ask someone to exchange skills with you
- **Real-time chat** once a connection is accepted

Built as a Flask web application for the UWA Agile Web Development unit.

---

## Team Members

| UWA ID | Name | GitHub Username |
|--------|------|-----------------|
| 24562775 | Sahil Pankajbhai Patel | [sahilppatel1807](https://github.com/sahilppatel1807) |
| 25039111 | Nandhukrishna Gujjalapudi | [NandhuKrishna001](https://github.com/NandhuKrishna001) |
| 24944854 | Qi Ding | [qid7182](https://github.com/qid7182) |
| 24336969 | Xiaotong Liu | [Karinaaa-Liu](https://github.com/Karinaaa-Liu) |

---

## Features

### Authentication & Account

- Sign up with name, nickname, email, password, course, and bio
- Secure login and logout (password hashing via Werkzeug)
- Account settings: change password, name, email, or delete account
- Login rate limiting to reduce brute-force attempts

### Profile & Skills

- Edit profile (name, course, bio)
- Add, edit, and delete skills you can teach
- Categorise skills (e.g. Programming, Design, Music)
- Optional skill level badges (Beginner, Intermediate, Expert)

### Discovery

- Browse all skills on the platform
- Filter by category
- Search by skill name or description

### Requests & Connections

- Send a skill exchange request from the Browse Skills page
- View incoming and outgoing requests on the Requests page
- Accept or decline incoming requests
- **Person-level connections:** once any request between two users is accepted, you are connected with that person — you can chat with them and all their other skills show as **Accepted** without sending separate requests

### Chat

- Message users you have an accepted connection with
- Connection sidebar and message history
- AJAX-based send and load (no page reload)

### Notifications

- Navbar badge for unseen incoming requests and unseen responses on sent requests

---

## Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | [Flask](https://flask.palletsprojects.com/) |
| ORM | [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) |
| Auth | [Flask-Login](https://flask-login.readthedocs.io/) |
| Forms & CSRF | [Flask-WTF](https://flask-wtf.readthedocs.io/) |
| Migrations | [Flask-Migrate](https://flask-migrate.readthedocs.io/) (Alembic) |
| Rate limiting | [Flask-Limiter](https://flask-limiter.readthedocs.io/) |
| Database | SQLite (default, local `instance/skillswap.db`) |
| Frontend | Jinja2 templates, custom CSS, [Bootstrap](https://getbootstrap.com/) (modals & layout), [Tabler Icons](https://tabler.io/icons) |
| Client JS | jQuery (AJAX for requests & chat) |
| E2E tests | [Selenium](https://www.selenium.dev/) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip`
- (Optional) Chrome/Chromium for Selenium end-to-end tests

### 1. Enter the project

```bash
cd Skillswap
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root with this fields.

```env
SECRET_KEY=dev-secret-key

# if you want you can enable the debug mode too.
FLASK_DEBUG=true
```
OR (put this in the CLI)
```
export SECRET_KEY=dev-secret-key
python app.py
```

`SECRET_KEY` is **required**. The app will not start without it.

### 5. Run the application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

On first run, the database is created automatically in `instance/skillswap.db`.

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | Flask session signing key |
| `FLASK_DEBUG` | No | `false` | Enable Flask debug mode (`true` / `false`) |
| `DATABASE_URL` | No | `sqlite:///…/instance/skillswap.db` | SQLAlchemy database URI |

Configuration is defined in `config.py`. Test configs (`TestConfig`, `SeleniumTestConfig`) use in-memory SQLite and are used only by the test suite.

---

## Project Structure

```
Skillswap/
├── app.py                 # Application entry point
├── __init__.py            # App factory, extensions, blueprints
├── config.py              # Environment-based configuration
├── models.py              # User, Skill, Request, Message models
├── forms.py               # WTForms for auth and settings
├── routes/
│   ├── main.py            # Home page
│   ├── auth.py            # Signup, login, logout, account settings
│   ├── skills.py          # Browse & post skills
│   ├── requests.py        # Send, accept, decline requests
│   ├── profile.py         # Profile & skill CRUD
│   └── chat.py            # Messaging between connected users
├── templates/             # Jinja2 HTML templates
├── static/
│   ├── css/               # Page-specific stylesheets
│   └── js/                # skills.js, chat.js, profile.js
├── migrations/            # Alembic database migrations
├── tests/
│   ├── unit_tests.py      # Unit / integration tests
│   └── selenium_tests.py  # Browser end-to-end tests
├── docs/
│   ├── user_stories.md
│   ├── test_cases.md
│   ├── test_report.md
│   └── database_er_diagram.md
├── instance/              # Local SQLite DB (gitignored)
└── requirements.txt
```

---

## How It Works

### Typical user flow

1. **Sign up** and create a profile.
2. **Add skills** you can teach from your Profile page.
3. **Browse Skills** to find what others offer — filter by category or search by keyword.
4. Click **Request** on a skill card to send an exchange request.
5. The skill owner sees the request under **Requests → Incoming** and can **Accept** or **Decline**.
6. Once accepted, both users appear in each other's **Chat** connections and can message freely.

### Person-level connections

Requests are stored per skill, but **connections are per person**:

- Accepting **one** request from a user accepts any other **pending** requests between you and that user.
- On Browse Skills, **all** skills from a connected user display **Accepted**.
- You cannot send a new request to someone you are already connected with.
- Chat access is based on whether **any** accepted request exists between two users (in either direction).

This avoids asking the same person multiple times when they list several skills.

### Request statuses

| Status | Meaning |
|--------|---------|
| `pending` | Waiting for the recipient to respond |
| `accepted` | Connection established — chat is available |
| `declined` | Recipient declined the request |

---

## Running Tests

Tests use in-memory SQLite and disable CSRF for simpler HTTP testing.

### Unit tests

```bash
python -m unittest tests.unit_tests -v
```

Run a single test class:

```bash
python -m unittest tests.unit_tests.RequestsTests -v
python -m unittest tests.unit_tests.ChatTests -v
```

### Selenium end-to-end tests

Requires Chrome and ChromeDriver available on your `PATH`. The test runner starts Flask on port **5001** automatically.

```bash
python -m unittest tests.selenium_tests -v
```

See [`docs/test_cases.md`](docs/test_cases.md) and [`docs/test_report.md`](docs/test_report.md) for the full test catalogue and results.

---

## Database & Migrations

### Default setup

For local development, `python app.py` runs `db.create_all()` and applies lightweight schema patches for existing databases — no manual migration step is required for a fresh clone.

### Alembic migrations (optional)

If you use Flask-Migrate for schema changes:

```bash
export FLASK_APP=app.py
flask db upgrade
```

### Data model

| Model | Purpose |
|-------|---------|
| `User` | Student accounts |
| `Skill` | Skills a user offers to teach |
| `Request` | Exchange requests (linked to a skill) |
| `Message` | Chat messages between connected users |

See [`docs/database_er_diagram.md`](docs/database_er_diagram.md) for the ER diagram and relationship details.

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/user_stories.md`](docs/user_stories.md) | User stories and acceptance criteria |
| [`docs/test_cases.md`](docs/test_cases.md) | Manual and automated test case definitions |
| [`docs/test_report.md`](docs/test_report.md) | Test execution report |
| [`docs/database_er_diagram.md`](docs/database_er_diagram.md) | Database schema overview |

---

## Main Routes

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/signup`, `/login`, `/logout` | Authentication |
| `/skills` | Browse, search, and filter skills |
| `/profile` | View profile and manage your skills |
| `/requests` | Incoming and sent exchange requests |
| `/chat` | Messaging with accepted connections |
| `/settings/*` | Change password, name, email; delete account |

---

## License

This project was developed as coursework for the University of Western Australia (UWA) Agile Web Development unit (CITS3403 / CITS5505).

Copyright © 2026 Sahil Pankajbhai Patel, Nandhukrishna Gujjalapudi, Qi Ding, and Xiaotong Liu.

All rights reserved. This repository is provided for academic assessment purposes. You may not copy, modify, or distribute this work without permission from the authors and UWA, except as required for unit marking.
