import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    # body = StringField("Blog Content", validators=[DataRequired()])
    body = CKEditorField(label="Blog Content")
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = db.session.query(BlogPost).filter_by(id=index).first()
    if requested_post:
        return render_template("post.html", post=requested_post)
    return redirect(url_for("get_all_posts"))


@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.session.query(BlogPost).filter_by(id=post_id).first()
    form = CreatePostForm(title=post.title,
                          subtitle=post.subtitle,
                          img_url=post.img_url,
                          author=post.author,
                          body=post.body
                          )
    if request.method == "GET":
        return render_template("make-post.html", form=form, new=False)
    post.title = form.title.data
    post.subtitle = form.subtitle.data
    post.body = form.body.data
    post.author = form.author.data
    post.img_url = form.img_url.data
    db.session.commit()
    return redirect(url_for("show_post", index=post.id))


@app.route("/new-post", methods=["POST", "GET"])
def new_post():
    form = CreatePostForm()
    if request.method == "GET":
        return render_template("make-post.html", form=form, new=True)
    date = datetime.datetime.today().strftime("%B %d, %Y")
    data = BlogPost(title=form.title.data,
                    subtitle=form.subtitle.data,
                    body=form.body.data,
                    author=form.author.data,
                    img_url=form.img_url.data,
                    date=date
                    )
    db.session.add(data)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

@app.route("/delete/<post_id>", methods=["POST", "GET"])
def delete_post(post_id):
    post = db.session.query(BlogPost).filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
