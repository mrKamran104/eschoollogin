from flask import Flask, render_template, request, session, g
from flask_sqlalchemy import SQLAlchemy
import os
import random

app = Flask(__name__)
user_found = ""
app.config['SECRET_KEY'] = 'the-random-string'
#app.secret_key = os.urandom(24)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "schooldb.db"))

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Users(db.Model):
    uname = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    role = db.Column(db.String(10), unique=False, nullable=False)


# db.create_all()

@app.route('/')
def index():
    global user_found
    if 'user' in session and session['user'] == user_found.uname:
        if user_found.role == "Teacher":
            return render_template('teacher.html', name=user_found.uname, role=user_found.role)
        elif user_found.role == "Student":
            return render_template('student.html', name=user_found.uname, role=user_found.role)
        else:
            return render_template('admin.html', name=user_found.uname, role=user_found.role)

    return render_template('index.html')


@app.route('/panel', methods=["POST", "GET"])
def admin():
    global user_found
    if request.method == "POST":
        uname = request.form['target_uname']
        pwrd = request.form['target_pass']
        user_found = Users.query.filter_by(uname=uname, password=pwrd).first()
        if user_found:
            session['user'] = uname
            if user_found.role == "Teacher":
                return render_template('teacher.html', name=uname, role=user_found.role)
            elif user_found.role == "Student":
                return render_template('student.html', name=uname, role=user_found.role)
            else:
                return render_template('admin.html', name=uname, role=user_found.role)
        else:
            return render_template('index.html')
    elif user_found != "":
        if user_found.role == "Teacher":
            return render_template('teacher.html', name=user_found.uname, role=user_found.role)
        elif user_found.role == "Student":
            return render_template('student.html', name=user_found.uname, role=user_found.role)
        else:
            return render_template('admin.html', name=user_found.uname, role=user_found.role)
    else:
        return render_template('index.html')


# @app.before_request
# def before_request():
#     g.user=None
#     if 'user' in session:
#         g.user = session['user']


@app.route('/editprofile', methods=["POST", "GET"])
def editprofile():
    global user_found
    if 'user' in session and session['user'] == user_found.uname:
        if 'UPDATE' in request.form.values():
            email = request.form['email']
            password = request.form['password']

            user_found.email = email
            user_found.password = password
            db.session.add(user_found)
            db.session.commit()
            return render_template('editprofile.html', uname=user_found.uname, email=user_found.email,
                                   pswrd=user_found.password, role=user_found.role)
        elif 'DELETE' in request.form.values():
            target_user = Users.query.filter_by(uname=user_found.uname).first()
            db.session.delete(target_user)
            db.session.commit()
            session.pop('user', None)
            return render_template('index.html')
        else:
            return render_template('editprofile.html', uname=user_found.uname, email=user_found.email,
                                   pswrd=user_found.password, role=user_found.role)

    return render_template('index.html')


@app.route('/AddorRemoveMember', methods=["POST", "GET"])
def AddorRemoveMember():
    global user_found
    if 'user' in session and session['user'] == user_found.uname:
        if 'Sign Up' in request.form.values():
            user = Users()
            user.uname = request.form['username']
            user.email = request.form['email']
            user.password = request.form['password']
            user.role = request.form['role']
            db.session.add(user)
            db.session.commit()
        elif 'UPDATE' in request.form.values():
            uname = request.form['uname']
            target_user = Users.query.filter_by(uname=uname).first()
            target_user.email = request.form['email']
            target_user.password = request.form['password']
            target_user.role = request.form['role']
            db.session.add(target_user)
            db.session.commit()
        elif 'DELETE' in request.form.values():
            user_name = request.form['uname']
            target_user = Users.query.filter_by(uname=user_name).first()
            db.session.delete(target_user)
            db.session.commit()
        pswrd = random.randint(1, 1000000)
        users = Users.query.all()
        return render_template('AddorRemoveMember.html', users=users, name=user_found.uname, role=user_found.role,
                               pswrd=pswrd)

    return render_template('index.html')


@app.route('/stdother')
def stdother():
    global user_found
    if 'user' in session and session['user'] == user_found.uname:
        return render_template('stdother.html', name=user_found.uname, role=user_found.role)

    return render_template('index.html')


@app.route('/tchrother')
def tchrother():
    global user_found
    if 'user' in session and session['user'] == user_found.uname:
        return render_template('tchrother.html', name=user_found.uname, role=user_found.role)
    return render_template('index.html')


@app.route('/logout')
def login():
    # if 'user' in session:
    session.pop('user', None)
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
