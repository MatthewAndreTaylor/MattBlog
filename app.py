from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_user, UserMixin, login_required
import hmac
import config
import re
from flask_session import Session

app = Flask(__name__)
app.secret_key = config.key
users = config.users
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email: str):
    if email not in users:
        return
    user = User()
    user.id = email
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    email = request.form["email"]
    if email in users and hmac.compare_digest(
        config.encode(str(request.form["password"])), users[email]["password"]
    ):
        user = User()
        user.id = email
        login_user(user)
        return redirect("/post")
    return redirect("/post")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Post %r>" % self.id


@app.route("/", methods=["GET"])
def index():
    posts = Post.query.order_by(Post.date_created.desc()).paginate(page=1, per_page=7)
    return render_template("index.html", posts=posts)


@app.route("/posts", methods=["GET"])
def posts():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_created.desc()).paginate(
        page=page, per_page=7
    )
    return render_template("partial_posts.html", posts=posts)


@app.route("/like_action/<int:post_id>/<action>", methods=["GET"])
def like_action(post_id, action):
    liked_posts = session.get("liked_posts", set())

    if action == "like":
        liked_posts.add(post_id)
    if action == "unlike":
        liked_posts.discard(post_id)

    session["liked_posts"] = liked_posts
    return "200"


@app.template_filter("is_liked")
def is_liked(post_id):
    return post_id in session.get("liked_posts", set())


@app.route("/post", methods=["POST", "GET"])
@login_required
def post():
    if request.method == "POST":
        post_title = request.form["title"]
        post_content = request.form["content"]
        new_post = Post(title=post_title, content=post_content)

        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect("/post")
        except:
            return "Sorry couldn't make the post"
    else:
        posts = Post.query.order_by(Post.date_created).all()
        return render_template("post.html", posts=posts)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    post_to_delete = Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect("/post")
    except:
        return "Sorry couldn't delete the post"


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]

        try:
            db.session.commit()
            return redirect("/post")
        except:
            return "Sorry couldn't edit the post"
    else:
        return render_template("edit.html", post=post)


@app.template_filter("tokenize")
def tokenize_post(content: str):
    pattern = r"<([^>]+)>(.*?)<\1>"
    matches = re.findall(pattern, content, re.DOTALL)
    return matches


if __name__ == "__main__":
    app.run()
