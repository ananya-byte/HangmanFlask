# 🎮 HangmanFlask — Multiplayer Hangman with Persistent Progress

A web-based Hangman game built with Flask and MySQL. Players sign up, log in, and work through a shared word bank — completed words are tracked per user so you never repeat yourself.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)

---

## ✨ Features

- User authentication with bcrypt password hashing
- Per-user progress tracking — completed words are excluded from future rounds
- Session-based game state (current word, guesses, remaining attempts)
- Signup / Login / Logout flows
- Win and loss result screens with play-again support

---

## 🗂 Project Structure

```
HangmanFlask/
├── app.py            # Main Flask application and route handlers
├── create_db.py      # Database initialisation script
├── templates/        # Jinja2 HTML templates (login, signup, game, result)
└── static/           # CSS and static assets
```

---

## 🛠 Setup

### Prerequisites
- Python 3.8+
- MySQL server running locally

### Installation

```bash
git clone https://github.com/ananya-byte/HangmanFlask.git
cd HangmanFlask
pip install flask flask-bcrypt mysql-connector-python
```

### Database Setup

```bash
# Create the database schema and seed the word bank
python create_db.py
```

### Configuration

> ⚠️ **Security note:** Before running, move credentials out of `app.py` into environment variables or a `.env` file. Never commit secrets to version control.

```python
# Replace hardcoded values in app.py with:
import os
app.secret_key = os.environ.get("SECRET_KEY")
db_config = {
    'host': os.environ.get("DB_HOST", "localhost"),
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get("DB_PASSWORD"),
    'database': 'hangman_db'
}
```

### Run

```bash
python app.py
# Visit http://localhost:5000/login
```

---

## 🧠 How It Works

1. Sign up and log in
2. Navigate to `/hangman` and click **New Game** to get a word
3. Guess letters one at a time — you have 6 attempts
4. Win or lose, the word is marked complete and won't appear again for your account
5. Play again to get a new word from the remaining pool

---

## 💡 What I Learned

- Flask session management and route protection
- MySQL integration with `mysql.connector` and parameterised queries
- Password hashing with `flask-bcrypt`
- Separating game state from UI logic using server-side sessions
