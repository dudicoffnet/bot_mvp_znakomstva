
import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        goals TEXT
    )''')
    conn.commit()
    conn.close()

def save_user(user_id, name, goals):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("REPLACE INTO users (user_id, name, goals) VALUES (?, ?, ?)", (user_id, name, ",".join(goals)))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT user_id, name, goals FROM users")
    users = c.fetchall()
    conn.close()
    return users

def find_matches(current_goals):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    query = "SELECT user_id, name, goals FROM users"
    c.execute(query)
    all_users = c.fetchall()
    conn.close()
    matches = []
    for user_id, name, goals_str in all_users:
        goals = goals_str.split(",")
        if set(current_goals).intersection(goals):
            matches.append((user_id, name, goals))
    return matches
