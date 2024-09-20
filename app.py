from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import random
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = 'ananya2002'
bcrypt = Bcrypt(app)
# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Chinnu@2002',
    'database': 'hangman_db'
}

# Database Connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

def load_words(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM words WHERE word NOT IN (SELECT word FROM completed WHERE username = %s)", (username,))
    words = cursor.fetchall()
    cursor.close()
    conn.close()
    print("Available words for user", username, ":", words)  # Debugging output
    return [word[0] for word in words]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()  # Fetch one row
        cur.close()
        conn.close()
        print(result)
        if result and bcrypt.check_password_hash(result[0], password) :
            session['username'] = username
            print('Login successful!', 'success')
            return redirect(url_for('homepg'))  # Redirect to the main game page
        else:
            print('Invalid username or password', 'danger')

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
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password))
            conn.commit()
            flash('Signup successful! You can log in now.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            conn.rollback()
        finally:
            cur.close()

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

    # Initialize session variables if not already set
    if 'word' not in session or session['word'] is None:
        session['word'] = None
    if 'guessed_letters' not in session:
        session['guessed_letters'] = []
    if 'attempts' not in session:
        session['attempts'] = 6
    print(request.method)
    if request.method == 'POST':
        available_words = load_words(session['username'])
        if available_words:  # Ensure there are words to choose from
            session['word'] = random.choice(available_words)
            session['attempts'] = 6  # Reset attempts
            session['guessed_letters'] = []  # Clear previous guesses
            session['last_guess'] = None  # Clear last guess
        else:
            session['word'] = None  # No words available
            flash('No available words to play with.', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html', word=session['word'], attempts=session['attempts'])

@app.route('/guess', methods=['POST'])
def guess():
    # Check if a word has been assigned
    if 'word' not in session or session['word'] is None:
        flash('No word has been assigned. Please start a new game.', 'danger')
        return redirect(url_for('index'))

    letter = request.form['letter'].lower()
    session['last_guess'] = letter  # Store the last guess

    # Check if the letter has already been guessed
    if letter in session['guessed_letters']:
        flash(f"You've already guessed the letter '{letter}'.", 'warning')
        return redirect(url_for('index'))

    if all(l in session['guessed_letters'] for l in session['word']):
        return redirect(url_for('result', success=True))

    session['guessed_letters'].append(letter)

    # Check if the letter is in the word
    if letter not in session['word']:
        session['attempts'] -= 1

    # Check win/lose conditions
    if session['attempts'] <= 0:
        # Logic for losing
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO completed (username, word) VALUES (%s, %s)", (session['username'], session['word']))
        conn.commit()
        cursor.close()
        return redirect(url_for('result', success=False))

    if all(char in session['guessed_letters'] for char in session['word']):
        # Logic for winning
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO completed (username, word) VALUES (%s, %s)", (session['username'], session['word']))
        conn.commit()
        cursor.close()
        return redirect(url_for('result', success=True))

    return redirect(url_for('index'))

@app.route('/play_again')
def play_again():
    session.pop('word', None)
    session.pop('attempts', None)
    session['guessed_letters'] = []  # Reset guessed letters
    session['last_guess'] = None  # Clear last guess
    return redirect(url_for('index'))

@app.route('/result')
def result():
    success = request.args.get('success') == 'True'
    print(request.args.get('success'))
    return render_template('result.html', success=success, word=session['word'])

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")  # Change to your table name
    results = cur.fetchall()
    cur.close()
    
    # Convert results to a list of dictionaries
    users = [{'username': row[0], 'emails': row[1]} for row in results]
    return users

if __name__ == '__main__':
    app.run(debug=True)
