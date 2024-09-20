import mysql.connector

def create_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Chinnu@2002'
    )
    cursor = conn.cursor()
    
    cursor.execute("CREATE DATABASE IF NOT EXISTS hangman_db")
    cursor.execute("USE hangman_db")

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)

    # Create words table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(255) NOT NULL
    )
    """)

    # Create completed table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completed (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        word VARCHAR(255) NOT NULL
    )
    """)

    # Insert example words
    example_words = ['python', 'flask', 'hangman', 'challenge', 'programming', 'adventure', 'mountain', 'river', 'music', 'creativity', 'travel', 'puzzle', 'friendship', 'universe', 'exploration', 'wisdom', 'courage', 'innovation', 'history', 'culture', 'literature', 'art', 'emotion', 'freedom', 'nature', 'discovery', 'imagination', 'passion', 'harmony', 'reflection']
    for word in example_words:
        cursor.execute("INSERT IGNORE INTO words (word) VALUES (%s)", (word,))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_db()

