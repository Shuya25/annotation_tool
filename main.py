import os
import pandas as pd
import base64
from flask import Flask, render_template, request, url_for


ROOT = '.'
INPUT_CSV = ROOT + '/data.csv'
DF = pd.read_csv(INPUT_CSV, index_col=0)
UPDATE_COL = set([1])
COL_NAME = {1: "label"}
for i in UPDATE_COL:
  DF[COL_NAME[i]] = -1
print(DF)


app = Flask(__name__)

forms = {
    'root': ROOT,
    'name': '',
    'index': 0,
    'num': 5,
    'out_csv': ''
}

def forms_update(start):
  global forms
  forms['index'] = start
  forms['paths'] = DF[start: start+forms['num']].path
  forms['images'] = [base64.b64encode(open(
      f'{ROOT}/images/{path}', 'rb').read()).decode('utf-8')
      for path in forms['paths']]
  #for c in UPDATE_COL
  labels = list(map(str, list(DF[start: start+forms['num']].label)))
  if all(label != '-1' for label in labels):
    forms['label'] = "".join(labels)
  else:
    forms['label'] = ''
  return 0

def csv_update(start, labels):
  global forms
  for u in UPDATE_COL:
    for i, l in enumerate(list(labels)):
      if l == '0' or l == '1':
        DF.iloc[start+i, u] = l
      else:
        return 1
  DF.to_csv(forms['out_csv'])
  return 0

@app.route('/')
def login():
  return render_template('login.html')


@app.route('/annotation', methods=['GET', 'POST'])
def annotation():
  global forms, DF
  if request.method == "GET":
    return render_template('annotation.html', forms=forms)
  elif request.method == "POST":
    forms['name'] = request.form['name']
    start = int(request.form['index'])
    forms['out_csv'] = f'{ROOT}/output_{forms["name"]}.csv'

    if os.path.exists(forms['out_csv']):
      DF = pd.read_csv(forms['out_csv'], index_col=0)

    forms_update(start)
    return render_template('annotation.html', forms=forms)


@app.route('/annotation/next', methods=['GET', 'POST'])
def annotation_next():
  global forms
  if request.method == "GET":
    return render_template('annotation.html', forms=forms)
  elif request.method == "POST":
    label1 = request.form['label1']
    if len(label1) != forms['num']:
      return render_template('annotation.html', forms=forms)

    start = forms['index']
    if csv_update(start, label1):
      return render_template('annotation.html', forms=forms)

    start += forms['num']
    forms_update(start)
    return render_template('annotation.html', forms=forms)


@app.route('/annotation/pre', methods=['GET'])
def annotation_pre():
  global forms
  if request.method == "GET":
    start = forms['index']
    start -= forms['num']
    if start < 0: start = 0
    forms_update(start)
    return render_template('annotation.html', forms=forms)


if __name__ == '__main__':
  app.run(host='localhost', port=3000, threaded=True)
  # app.run(host='0.0.0.0', port=3001, threaded=True)
