import os

from flask import Flask, render_template_string, render_template, redirect, flash, request, Response
from flask_mail import Mail
from flask_security import Security, current_user, auth_required, hash_password, \
     SQLAlchemySessionUserDatastore, login_required
from flask_wtf import CSRFProtect

import dbmanager
from forms import *

import config
from dbmanager import *

# Create app
app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object(config)
mail = Mail(app)

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def create_user():
    init_db()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(email="test@me.com", password=hash_password("password"), username="alpha")
    db_session.commit()


# Views
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/canvas/<canvas_id>", methods=['GET'])
def preview_canvas(canvas_id):
    if request.method == "GET":
        try:
            return render_template("canvas_preview.html", canvas=get_canvas(canvas_id))
        except CanvasNotFoundError:
            return render_template("invalid_canvas.html")


@app.route("/canvas/<canvas_id>/edit", methods=['GET', 'POST'])
def edit_canvas(canvas_id):
    if request.method == "GET":
        try:
            return render_template("canvas_preview.html", canvas=get_canvas(canvas_id))
        except CanvasNotFoundError:
            return render_template("invalid_canvas.html")


@app.route('/create_canvas', methods=['GET', 'POST'])
def create_canvas():
    if not current_user.is_authenticated:
        return redirect("/")
    form = CanvasCreationForm()
    print(form.validate_on_submit())
    flash(form.errors)
    if form.validate_on_submit():
        dbmanager.create_canvas(form.id.data, current_user.id, form.max_paint.data, form.paint_regen.data,
                                form.allow_anonymous.data, CanvasAccess.PUBLIC)
        return redirect(f'/canvas/{form.id.data}')
    return render_template('create_canvas.html', form=form)


@app.route("/user/<user_id>")
def user(user_id):
    target_user = user_datastore.find_user(id=user_id)
    return render_template("user.html", user=target_user)


@app.route("/browse")
def browse():
    return render_template("browse.html")


@app.route("/group/<group_id>")
def group(group_id):
    return render_template("group.html", group_id=group_id)


if __name__ == '__main__':
    app.run()
