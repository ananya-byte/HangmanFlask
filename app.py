import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import random
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
bcrypt = Bcrypt(app)

# Database Configuration
db_config = {
    'host': os.environ.get("DB_HOST", "localhost"),
    'user': os.environ.get("DB_USER", "root"),
    'password': os.environ.get("DB_PASSWORD"),
    'database': os.environ.get("DB_NAME", "hangman_db"),
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


def load_words(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT word FROM words WHERE word NOT IN "
        "(SELECT word FROM completed WHERE username = %s)",
        (username,)
    )
    words = cursor.fetchall()
    cursor.close()
    conn.close()
    return [word[0] for word in words]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and bcrypt.check_password_hash(result[0], password):
            session['username'] = username
            return redirect(url_for('homepg'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()
            flash('Signup successful! You can log in now.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    return render_template('signup.html')


@app.route('/homepage')
def homepg():
    return render_template('homepage.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/hangman', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    session.setdefault('word', None)
    session.setdefault('guessed_letters', [])
    session.setdefault('attempts', 6)

    if request.method == 'POST':
        available_words = load_words(session['username'])
        if available_words:
            session['word'] = random.choice(available_words)
            session['attempts'] = 6
            session['guessed_letters'] = []
            session['last_guess'] = None
        else:
            session['word'] = None
            flash('No available words to play with.', 'danger')
        return redirect(url_for('index'))

    return render_template('index.html', word=session['word'], attempts=session['attempts'])


@app.route('/guess', methods=['POST'])
def guess():
    if 'word' not in session or session['word'] is None:
        flash('No word has been assigned. Please start a new game.', 'danger')
        return redirect(url_for('index'))

    letter = request.form['letter'].lower()
    session['last_guess'] = letter

    if letter in session['guessed_letters']:
        flash(f"You've already guessed '{letter}'.", 'warning')
        return redirect(url_for('index'))

    session['guessed_letters'].append(letter)

    if letter not in session['word']:
        session['attempts'] -= 1

    word_complete = all(char in session['guessed_letters'] for char in session['word'])
    out_of_attempts = session['attempts'] <= 0

    if word_complete or out_of_attempts:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO completed (username, word) VALUES (%s, %s)",
            (session['username'], session['word'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('result', success=word_complete))

    return redirect(url_for('index'))


@app.route('/play_again')
def play_again():
    session.pop('word', None)
    session.pop('attempts', None)
    session['guessed_letters'] = []
    session['last_guess'] = None
    return redirect(url_for('index'))


@app.route('/result')
def result():
    success = request.args.get('success') == 'True'
    return render_template('result.html', success=success, word=session.get('word'))


if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
