import datetime

import flask
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pword@localhost/DBProj'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    github_id = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    date_joined = db.Column(db.Date(), default=datetime.datetime.now())
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, github):
        self.username = username
        self.password = password
        self.github_id = github

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    @classmethod
    def get(cls, id):
        return cls.query.get(id)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(120))
    caretaker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    caretaker = db.relationship('User')
    tags = db.Column(db.String(255))
    github_repo = db.Column(db.String(255))
    description = db.Column(db.Text())
    date_added = db.Column(db.Date(), default=datetime.datetime.now())

    def __init__(self, name, repo, description, caretaker_id=None):
        self.project_name = name
        self.github_repo = repo
        self.description = description
        self.caretaker_id = caretaker_id
        self.tags = ''
        if caretaker_id:
            #import ipdb;
            #ipdb.set_trace()
            user = User.query.get(caretaker_id)
            self.caretaker = user
        else:
            self.caretaker = None




    def __repr__(self):
    	return '<Project {}>'.format(self.project_name)

    def to_dict(self):
        return {
            'name': self.project_name,
            'github_repo': self.github_repo,
            'description': self.description
        }


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    top_projects = sorted(Project.query.all()[:10], key=lambda p: p.date_added, reverse=True)
    return render_template('home.html', top_projects=top_projects)


@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'GET':
        return render_template('new_project.html')
    else:
        j = request.get_json()
        # Probably should handle exceptions
        proj = Project(j['name'], j['link'], j['description'], caretaker_id=j['caretaker_id'])
        db.session.add(proj)
        db.session.commit()
        return jsonify(proj.to_dict())


@app.route('/projects/<pid>', methods=['GET', 'DELETE'])
def view_project(pid):
    proj = Project.query.get(pid)
    if request.method == 'DELETE':
        db.session.delete(proj)
        db.session.commit()
        return jsonify({
            'success': True
        })
    else:
        return render_template('view_project.html', project=proj)


@app.route('/users/<uid>')
def view_user(uid):
    user = User.get(uid)
    # owns = db.engine.execute("select * from project where caretaker_id = {} limit 10".format(user.id))
    owns = Project.query.filter_by(caretaker_id=user.id).limit(10)
    return render_template('view_user.html', user=user, owns=list(owns))

@app.route('/tags/<tag>', methods=['GET', 'DELETE'])
def view_project_tag(tag):
    #proj = Project.query.filter(tags = tag)
    proj = db.engine.execute("select * from project where tags like '%%{0}%%'".format(tag))
    
    if request.method == 'DELETE':
        db.session.delete(proj)
        db.session.commit()
        return jsonify({
            'success': True
        })
    else:
        return render_template('view_project_tag.html', tag_projects=proj, tag_name = tag)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Login and validate the user.
        user = User(
            form.username.data,
            form.password.data,
            form.github_id.data
        )
        try:
            db.session.add(user)
            db.session.commit()
        except:
            flask.flash('Username already taken')
        login_user(user)
        flask.flash('Logged in successfully.')

        return flask.redirect(flask.url_for('index'))
    return flask.render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user.password == form.password.data:
            login_user(user)
            flask.flash('Logged in successfully.')

            return flask.redirect(flask.url_for('index'))
        else:
            flask.flash('Incorrect username and password')
    return flask.render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    db.init_app(app)
    db.create_all()
    app.run(debug=True)
