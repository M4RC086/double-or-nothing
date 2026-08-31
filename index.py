#!/bin/python
from flask import Flask, render_template, jsonify
from random import choice

BEGIN_RANDOM_MIN = 80
score = 10


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("game.html", score=score)



@app.route('/change-score', methods=['POST'])
def changeScore(): 
    global score

    the_ultimate_choice = choice([True, True, True, True, False])

    if (the_ultimate_choice or score <= BEGIN_RANDOM_MIN):
        score *= 2
    else:
        score = 20


    str_score = "$"+str(score)
    return jsonify({"new_value": str_score})# It does some js stuff I'm afraid of

@app.route('/stay', methods=['POST'])
def stay():
    global score
    score = 20
    return "score updated :)"


def get_db_score():
    # Get the score from the database
    pass

def set_db_score():
    # Change the score of the database
    pass


app.run(debug=True, host="0.0.0.0", port=5000)