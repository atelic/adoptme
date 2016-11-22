import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    github_id = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    date_joined = db.Column(db.Date(), default=datetime.datetime.now())

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(120))
    caretaker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    caretaker = db.relationship('User')
    tags = db.Column(db.String(255))
    github_repo = db.Column(db.String(255))
    description = db.Column(db.Text())

    def __init__(self, name, repo, description):
        self.project_name = name
        self.github_repo = repo
        self.description = description

    def __repr__(self):
        return '<Project {}'.format(self.project_name)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    return render_template('new_project.html')

if __name__ == '__main__':
    app.run()
