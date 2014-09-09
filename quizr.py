# -*- coding: utf-8 -*-
"""
Quizr - a quiz application created with Flask.
"""

import os
from flask import Flask, session, request, render_template, redirect, url_for

import io
import csv
import random
import time


# create app and initialize config
app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('QUIZR_SETTINGS', silent=True)


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    """
    Welcome page - quiz info and username form.
    """
    username = session.get('username')
    session['question_no'] = None 
    session['question_set'] = None
    session['correct_cnt'] = None
    
    if request.method == 'POST':
        if not username:
            username = session['username'] = request.form['username']
        if username:
            return redirect(url_for('question_page'))

    return render_template('welcome.html', username=username)


questionAskNo = 5
possible_answers = ['A', 'B', 'C', 'D', 'E', 'F']

def getAnswer(idx):
    return possible_answers[idx]

def pickQuestions(minNo, maxNo, cnt):   #numery pytan pomiedzy minNo-maxNo, cnt - ile pytan
    random.seed(time)
    indices = []
    if (maxNo - minNo + 1) < cnt:   #cnt required cannot be larger than given range
        return indices
    while len(indices) < cnt:
        x = random.randint(minNo-1, maxNo-1)
        if x not in indices:
            indices.append(x)
    
    return indices
    
def getQuizData():
    with io.open('data/quiz.csv', 'rb') as quizDataFile:
        quiz_data = csv.reader(quizDataFile, delimiter=';')
        q_list = []
        for line in quiz_data:
            q = [unicode(item, 'utf-8') for item in line]
            q_list.append(q)
        
        q_nums = pickQuestions(1, len(q_list), questionAskNo)
        q_selected = []
        for idx in q_nums:
            q_selected.append(q_list[idx])
        return q_selected


@app.route('/pytanie', methods=['GET', 'POST'])
def question_page():
    """
    Quiz question page - show question, handle answer.
    """
    # ToDo
    if request.method == "POST":
        ansIdx = int(request.form["answer"])
        if session['correct_ans'] == getAnswer(ansIdx):
            if not session['correct_cnt']:
                session['correct_cnt'] = 1
            else:
                session['correct_cnt'] = session['correct_cnt'] + 1
            
    q_cnt = session.get('question_no')
    q_list = session.get('question_set')
    if not q_list:
        q_list = session['question_set'] = getQuizData()
        q_cnt = session['question_no'] = 0
        
    if q_list and q_cnt < len(q_list):
        question =  q_list[q_cnt][0]
        session['correct_ans'] = correct = q_list[q_cnt][-1]
        answers = q_list[q_cnt][1:-1]
        session['question_no'] = q_cnt + 1
        return render_template('question.html', index = q_cnt+1, Question = question, Answers = answers, enumarate = enumerate)
    else:
        return redirect(url_for('result_page'))



@app.route('/wynik')
def result_page():
    """
    Last page - show results.
    """
    # ToDo
    percent = int( float(session['correct_cnt']) / float(questionAskNo) * 100)
    result = str(session['correct_cnt']) +' / ' +str(questionAskNo)
    return render_template('result.html', result = result, percent = percent)

if __name__ == '__main__':
    #app.run(host="0.0.0.0")
    app.debug = True
    app.run(host=os.environ['IP'], port=int(os.environ['PORT']))


