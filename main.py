import datetime

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from time import strftime


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap5(app)

ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


class AddForm(FlaskForm):
    post_title = StringField("Blog post Title",validators=[DataRequired()])
    subtitle = StringField("Subtitle",validators=[DataRequired()])
    your_name = StringField("Your Name",validators=[DataRequired()])
    img_url = StringField("Blog Image URL",validators=[DataRequired()])
    blog_content = CKEditorField("Blog Content",validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/view/<post_id>', methods=['GET','POST'])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost,post_id)
    return render_template("post.html", post=requested_post)


@app.route('/add', methods=['GET', 'POST'])
def add_new_post():
    form = AddForm()
    current_date = date.today().strftime("%B %d, %Y")

    if form.validate_on_submit():
        new_post = BlogPost(title=form.post_title.data,
                            subtitle=form.subtitle.data,
                            date=current_date,
                            body=form.blog_content.data,
                            author=form.your_name.data,
                            img_url=form.img_url.data)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))



    return render_template("make-post.html", form=form)


@app.route('/edit-post/<post_id>',methods=['GET', 'POST'])
def edit_post(post_id):

    post = db.get_or_404(BlogPost, post_id)
    edit_form = AddForm(post_title=post.title,
                        subtitle=post.subtitle,
                        your_name=post.author,
                        img_url=post.img_url,
                        blog_content=post.body)

    if edit_form.validate_on_submit():
        post.title = edit_form.post_title.data
        post.subtitle = edit_form.subtitle.data
        post.body = edit_form.blog_content.data
        post.author = edit_form.your_name.data
        post.img_url = edit_form.img_url.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route('/delete/<post_id>')
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
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
    app.run(debug=True, port=5003)
