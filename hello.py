from flask import Flask
from flask import make_response, redirect, abort, render_template
from flask_script import Manager


app = Flask(__name__)
manager = Manager(app)


@app.route('/')
def index():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response


@app.route('/abort')
def get_user():
    abort(404)
    return '<h1>This page is aborted.</h1>'


@app.route('/rdr')
def rdr():
    return redirect('http://www.baidu.com', 302)


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name


if __name__ == "__main__":
    manager.run()