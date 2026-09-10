#!/bin/python
from flask import Flask, render_template, jsonify, request, session, redirect
from random import choice
from os import urandom, getenv
from dotenv import load_dotenv
import psycopg2

BEGIN_RANDOM_MIN = 80
score = 20

app = Flask(__name__)
app.secret_key = urandom(24)

load_dotenv()
SUPABASE_URL = getenv("DATABASE_URL")

@app.route("/")
def login():
    if session.get("verified"):
        return redirect("/game")

    return render_template("login.html")


@app.route("/game")
def game():
    if not session.get("verified"):
        return redirect("/")

    return render_template("game.html", score=get_db_score(session['username']), username=session['username'])



# -- APIs for the frontend --
@app.route('/api/flip-coin', methods=['POST'])
def flipCoin(): 
    score = get_db_score(session["username"])
    
    is_win = choice([True, True, True, False])
    if (is_win or score <= BEGIN_RANDOM_MIN):
        score *= 2
        is_win = True
    else:
        score = 20
    

    set_db_score(session["username"], score)

    return jsonify({"isWin": is_win, "new_score": score})


@app.route('/api/login-username', methods=['POST'])
def loginUsername():
    
    
    data = request.get_json()

    
    if not all(char == ' ' for char in data.get("username")):
        username = data.get("username")

        session['username'] = username
        session['verified'] = True

        create_db_user(session['username'])

        return jsonify({"redirect": "/game", "error": False})
    return jsonify({"error": True})


@app.route("/api/get-leaderboard")
def getLeaderboard():
    return jsonify({"leaderboard": get_db_leaderboard(), "username":session['username']})



#-- DATABASE --
def _db_connection():
    conn = psycopg2.connect(SUPABASE_URL)
    return conn


def init_db():
    conn = _db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            username TEXT,
            score INTEGER
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def get_db_leaderboard():
    conn = _db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def get_db_score(user):
    conn = _db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM stats WHERE username = %s", (user,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None  
    return row[0]


def set_db_score(user, new_score):
    conn = _db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE stats SET score = %s WHERE username = %s", (new_score, user))

    conn.commit()
    cursor.close()
    conn.close()


def create_db_user(new_user):
    conn = _db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats WHERE username = %s", (new_user,))
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO stats (username, score) VALUES (%s, %s)", (new_user, 20))
        conn.commit()

    cursor.close()
    conn.close()
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
    