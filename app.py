from flask import Flask, request, render_template, redirect, url_for
from momir import *

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template('momir_form.html')

@app.route("/print", methods=["POST"])
def momir_print():
    if request.method == "POST":
        print(request.form.keys())
        input_num = int(request.form['input_num'])
        print_momir(input_num, False)
    
    return redirect(url_for('index'))

