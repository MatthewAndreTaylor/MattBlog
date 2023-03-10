from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_user, UserMixin, login_required
import os
import hmac
import random

import config

app = Flask(__name__)
app.secret_key = config.secret_salt + str(os.urandom(32))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

users = config.accounts


class User(UserMixin):
    pass


def encode(s: str) -> str:
    random.seed(s)
    return "".join(random.choice("HDSORMCasdwfegrjgovncxer19854nd")
                   for _ in range(45))


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    if email in users and hmac.compare_digest(encode(request.form['password']),
                                              users[email]['password']):
        user = User()
        user.id = email
        login_user(user)
        return redirect('/post')
    return redirect('/post')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.id


@app.route('/', methods=['GET'])
def index():
    posts = Post.query.order_by(Post.date_created.desc()).limit(15).all()
    return render_template('index.html', posts=posts)


@app.route('/more', methods=['GET'])
def more():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/post', methods=['POST', 'GET'])
@login_required
def post():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        new_post = Post(title=post_title, content=post_content)

        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect('/post')
        except:
            return "Sorry couldn't make the post"

    else:
        posts = Post.query.order_by(Post.date_created).all()
        return render_template('post.html', posts=posts)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post_to_delete = Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect('/post')
    except:
        return "Sorry couldn't delete the post"


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/post')
        except:
            return "Sorry couldn't edit the post"

    else:
        return render_template('edit.html', post=post)


if __name__ == "__main__":
    app.run()
