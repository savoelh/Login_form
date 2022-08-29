from flask import Flask, request, render_template, redirect, flash, session
from flask_mail import Mail, Message
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, PasswordResetForm, PasswordResetPassword
import secrets

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'シーッ,それは秘密です'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['MAIL_SERVER']='smtp.sendgrid.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
connect_db(app)
db.create_all()
token = ""

@app.route("/")
def front_page():
    """base page"""
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def registration():
    """Adds new user to database"""
    form = RegisterForm()
    if "username" in session:
        return redirect("/")
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.commit()
        session['username'] = new_user.username
        flash('You have created a new account')
        return redirect("/")
    return render_template('register.html', form=form)


@app.route("/users/<username>")
def secret_page(username):
    """Renders User page"""
    user = User.query.filter_by(username=username).first()
    if "username" not in session:
        flash("You are not authorized to access these very serious documents.")
        return redirect("/")
    elif user is None:
        return redirect("/")
    elif user.username == session['username']:
        form = FeedbackForm()
        return render_template("secret.html", user=user, form=form)
    else:
        return render_template("404.html")

@app.route("/logout")
def logout():
    """Log out function"""
    session.pop("username")
    return redirect("/")

@app.route("/login", methods=["POST", "GET"])
def login():
    """checks db for valid user and adds to session"""
    if "username" in session:
        return redirect("/users/<username>")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session["username"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Bad username / password"]      
    return render_template("login.html", form=form)

@app.route("/users/<username>/feedback/add", methods=["POST"])
def add_feedback(username):
    """ populates html and database with feedback data"""
    if "username" not in session:
        flash("You are not authorized to access these very serious documents.")
        return redirect("/")
    else: 
        form = FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            return redirect(f"/users/{new_feedback.username}")

@app.route("/users/<username>/<int:id>/edit")
def edit_feedback(username, id):
    if "username" not in session:
        flash("You are not authorized to access these very serious documents.")
        return redirect("/")
    else:
        this_feedback = Feedback.query.get(id)
        form = FeedbackForm()
        return render_template("feedback_edit.html", username=username, this_feedback = this_feedback,  form = form)

@app.route("/users/<username>/<int:id>/edit_submit", methods=["POST"])
def submit_feedback(username, id):
    this_feedback = Feedback.query.get(id)
    form = FeedbackForm()
    if form.validate_on_submit():
        this_feedback.title = form.title.data
        this_feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{username}")

@app.route("/users/<username>/<int:id>/delete", methods=["GET"])
def delete_feedback(username, id):
    feedback = Feedback.query.get(id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{username}')

@app.route("/users/<username>/delete")
def delete_user(username):
    user = User.query.get(username)
    session.pop("username")
    db.session.delete(user)
    db.session.commit()
    return redirect("/")

@app.route("/password_reset_form")
def password_reset_form():
    """renders pw reset form"""
    form = PasswordResetForm()
    return render_template("password_reset.html", form=form)

@app.route("/password_reset_action", methods=["POST", "GET"])
def password_reset():
    """Create token for pw reset and send email link"""
    form = PasswordResetForm()
    if form.validate_on_submit():
        email_entry = form.email.data
        email = User.query.filter_by(email=email_entry).first()
        if email is None:
            flash("The email you entered was not found in our database or there was an error.")
            return redirect("/password_reset_form")
        if email_entry == email.email:
            token = secrets.token_urlsafe()
            msg = Message(f"Here is your password reset link:",
                sender="savoeauto@gmail.com",
                recipients=[f"{email.email}"])
            msg.body=f"Please click the following link: http://127.0.0.1:5000/pw_reset_{token}"
            mail.send(msg)
            return redirect("/")
        else:
            flash("There was an unknown error.")
            return redirect("/password_reset_form")

@app.route("/pw_reset_<token>")
def pw_reset_page(token):
    """Renders page with token as the URL"""
    form = PasswordResetPassword()
    return render_template("reset.html", form=form)

@app.route("/password_reset_final", methods=["POST", "GET"])
def pw_reset_final():
    """Hashes PW and saves it to the DB"""
    form = PasswordResetPassword()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        this_user = User.query.filter_by(email=email).first()
        hashed = User.new_password(password)
        this_user.password = hashed
        db.session.commit()
        return redirect("/")
