import os

from flask import Flask, render_template_string, render_template, redirect, flash, request, Response
from flask_mail import Mail
from flask_security import Security, current_user, auth_required, hash_password, \
    SQLAlchemySessionUserDatastore, login_required
from flask_socketio import SocketIO, emit
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
socketio = SocketIO(app)

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT",
                                                      '146585145368132386173505678016728509634')

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


prepped_canvases = []


def on_connect(data):
    canvas = Canvas.query.filter_by(id=request.namespace.replace("/", "")).first()
    if canvas is None:
        raise CanvasNotFoundError(f"No canvas with id {request.namespace} could be found")
    marks = [mark.to_dict() for mark in Mark.query.filter_by(canvas=canvas).all()]
    emit("load_canvas", marks)


def on_mark(json):
    # calculate paint cost
    cost = math.floor(json["lineWidth"] *
                      (1 + math.dist([json["startPos"]["x"], json["startPos"]["y"]],
                                     [json["endPos"]["x"], json["endPos"]["y"]])))
    canvas = Canvas.query.filter_by(id=request.namespace.replace("/", "")).first()
    if canvas is None:
        raise CanvasNotFoundError(f"No canvas with id {request.namespace} could be found")
    paint_level = current_user.get_paint_level(canvas)
    if paint_level is None:
        paint_level = UserPaintLevel(user=current_user, canvas=canvas, level=canvas.max_paint,
                                     last_updated_at=datetime.datetime.utcnow())
        current_user.paint_levels.append(paint_level)
        db_session.add(paint_level)
    if paint_level.reduce_paint_level(cost):  # if user has proper paint levels
        mark = Mark(canvas=canvas, startX=json["startPos"]["x"], startY=json["startPos"]["y"],
                    endX=json["endPos"]["x"], endY=json["endPos"]["y"], color=json["color"],
                    lineWidth=json["lineWidth"], lineCap=json["lineCap"], marker=current_user)
        # TODO: Prevent users from flooding with data that causes an error, or at least make it recover cleanly from
        #  an error
        db_session.add(mark)
        db_session.commit()
        emit("mark_sync", mark.to_dict(), broadcast=True)
    emit("user_sync", {
        "paintLevel": paint_level.level
    })


def prep_canvas(canvas_id):
    if canvas_id not in prepped_canvases:
        socketio.on_event("mark", on_mark, namespace="/" + canvas_id)
        socketio.on_event("connect", on_connect, namespace="/" + canvas_id)


@app.route("/canvas/<canvas_id>", methods=['GET'])
def preview_canvas(canvas_id):
    prep_canvas(canvas_id)
    if request.method == "GET":
        try:
            return render_template("canvas_preview.html", canvas=get_canvas(canvas_id))
        except CanvasNotFoundError:
            return render_template("invalid_canvas.html")


@app.route("/canvas/<canvas_id>/edit", methods=['GET', 'POST'])
def edit_canvas(canvas_id):
    prep_canvas(canvas_id)
    if request.method == "GET":
        try:
            return render_template("canvas_edit.html", canvas=get_canvas(canvas_id))
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
        dbmanager.create_canvas(form.id.data, current_user.id, form.max_paint.data, 4000, 4000, 10000, 5,
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
    socketio.run(app)
