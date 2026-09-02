#!/bin/python
from flask import Flask, render_template, jsonify
from random import choice
import sqlite3

BEGIN_RANDOM_MIN = 80
score = 20
USER="M4RC086"

app = Flask(__name__)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/game")
def main():
    return render_template("game.html", score=get_db_score("M4RC086"))

@app.route('/change-score', methods=['POST'])
def changeScore(): 
    score = get_db_score(USER)

    the_ultimate_choice = choice([True, True, True, True, False])
    if (the_ultimate_choice or score <= BEGIN_RANDOM_MIN):
        score *= 2
    else:
        score = 20
    

    set_db_score(USER, score)

    str_score = "$"+str(score)
    return jsonify({"new_value": str_score})# It does some js stuff I'm afraid of


#-- DATABASE --

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("stats.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

def get_db_score(user):
    conn = db_connection()
    cursor = conn.cursor()

    cur = cursor.execute(f"SELECT score FROM stats WHERE user = '{user}'")
    conn.commit()
    return cur.fetchall()[0][0]
    

def set_db_score(user, new_score):
    conn = db_connection()
    cursor = conn.cursor()

    cur = cursor.execute(f"UPDATE stats SET score = {new_score} WHERE user = '{user}'")
    conn.commit()
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    