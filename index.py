#!/bin/python
from flask import Flask, render_template, jsonify, request, session, redirect
from random import choice
import os
import sqlite3

BEGIN_RANDOM_MIN = 80
score = 20

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def login():
    if session.get("verified"):
        return redirect("/game")

    return render_template("login.html")


@app.route("/game")
def game():
    if not session.get("verified"):
        print("not veryfsd")
        return redirect("/")

    return render_template("game.html", score=get_db_score(session['username']))


@app.route('/change-score', methods=['POST'])
def changeScore(): 
    score = get_db_score(session["username"])

    the_ultimate_choice = choice([True, True, True, True, False])
    if (the_ultimate_choice or score <= BEGIN_RANDOM_MIN):
        score *= 2
    else:
        score = 20
    

    set_db_score(session["username"], score)

    str_score = "$"+str(score)
    return jsonify({"new_value": str_score})# It does some js stuff I'm afraid of


@app.route('/login-username', methods=['POST'])
def loginUsername():
    

    data = request.get_json()
    username = data.get("username")
    print(username)
    
    session['username'] = username
    session['verified'] = True

    create_db_user(session['username'])
    

    return jsonify({"redirect": "/game"})



#-- DATABASE --


def init_db():
    conn = _db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            user TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def _db_connection():
    conn = None
    try:
        conn = sqlite3.connect("stats.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

def get_db_score(user):
    conn = _db_connection()
    cursor = conn.cursor()

    cur = cursor.execute(f"SELECT score FROM stats WHERE user = '{user}'")
    conn.commit()
    return cur.fetchall()[0][0]
    

def set_db_score(user, new_score):
    conn = _db_connection()
    cursor = conn.cursor()

    cur = cursor.execute(f"UPDATE stats SET score = {new_score} WHERE user = '{user}'")
    conn.commit()

def create_db_user(new_user):
    conn = _db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats WHERE user = ?", (new_user,))
    result = cursor.fetchone()

    if not result:
        cur = cursor.execute(f"INSERT INTO stats VALUES ('{new_user}', 20);")
        conn.commit()
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
    