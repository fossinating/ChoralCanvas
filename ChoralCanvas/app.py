import datetime
import math
import os
from flask import Flask, render_template_string, render_template, redirect, flash, request, Response
from flask_mail import Mail
from flask_security import Security, current_user, auth_required, hash_password, \
    SQLAlchemySessionUserDatastore, login_required
from flask_socketio import SocketIO, emit
from flask_wtf import CSRFProtect

from exc import CanvasNotFoundError
from forms import *
import config
from models import db, User, Role, UserCanvasProfile, Canvas, Mark, CanvasAccess
import database

# Create app
app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object(config)
mail = Mail(app)
socketio = SocketIO(app)
db.init_app(app)

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT",
                                                      '146585145368132386173505678016728509634')

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def create_user():
    database.init_db()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(email="test@me.com", password=hash_password("password"), username="alpha")
    db.session.commit()


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


def get_user_canvas_profile(user_obj, canvas_obj):
    profile = UserCanvasProfile.query.filter_by(user_id=user_obj.id, canvas_id=canvas_obj.id).first()
    if profile is None:
        profile = UserCanvasProfile(user=user_obj, canvas=canvas_obj, level=canvas_obj.max_paint,
                                    last_updated_at=datetime.datetime.utcnow())
        current_user.profiles.append(profile)
        db.session.add(profile)
    return profile


def on_marks(marks):
    accepted_marks = []
    for mark in marks:
        # calculate paint cost
        cost = math.floor(mark["lineWidth"] *
                          (1 + math.dist([mark["startPos"]["x"], mark["startPos"]["y"]],
                                         [mark["endPos"]["x"], mark["endPos"]["y"]])))
        canvas = Canvas.query.filter_by(id=request.namespace.replace("/", "")).first()
        if canvas is None:
            raise CanvasNotFoundError(f"No canvas with id {request.namespace} could be found")
        profile = get_user_canvas_profile(current_user, canvas)
        if profile.reduce_paint_level(cost):  # if user has proper paint levels
            mark = Mark(canvas=canvas, startX=mark["startPos"]["x"], startY=mark["startPos"]["y"],
                        endX=mark["endPos"]["x"], endY=mark["endPos"]["y"], color=mark["color"],
                        lineWidth=mark["lineWidth"], lineCap=mark["lineCap"], marker=current_user)
            # TODO: Prevent users from flooding with data that causes an error, or at least make it recover cleanly from
            #  an error
            db.session.add(mark)
            db.session.commit()
            accepted_marks.append(mark.to_dict())
        else:
            break

    emit("marks_sync", accepted_marks, broadcast=True)
    emit("user_sync", {
        "paintLevel": profile.level
    })


def on_mark(json):
    # calculate paint cost
    cost = math.floor(json["lineWidth"] *
                      (1 + math.dist([json["startPos"]["x"], json["startPos"]["y"]],
                                     [json["endPos"]["x"], json["endPos"]["y"]])))
    canvas = Canvas.query.filter_by(id=request.namespace.replace("/", "")).first()
    if canvas is None:
        raise CanvasNotFoundError(f"No canvas with id {request.namespace} could be found")
    profile = get_user_canvas_profile(current_user, canvas)
    if profile.reduce_paint_level(cost):  # if user has proper paint levels
        mark = Mark(canvas=canvas, startX=json["startPos"]["x"], startY=json["startPos"]["y"],
                    endX=json["endPos"]["x"], endY=json["endPos"]["y"], color=json["color"],
                    lineWidth=json["lineWidth"], lineCap=json["lineCap"], marker=current_user)
        # TODO: Prevent users from flooding with data that causes an error, or at least make it recover cleanly from
        #  an error
        db.session.add(mark)
        db.session.commit()
        emit("mark_sync", mark.to_dict(), broadcast=True)
    emit("user_sync", {
        "paintLevel": profile.level
    })


def prep_canvas(canvas_id):
    if canvas_id not in prepped_canvases:
        socketio.on_event("mark", on_mark, namespace="/" + canvas_id)
        socketio.on_event("marks", on_marks, namespace="/" + canvas_id)
        socketio.on_event("connect", on_connect, namespace="/" + canvas_id)


@app.route("/canvas/<canvas_id>", methods=['GET'])
def preview_canvas(canvas_id):
    prep_canvas(canvas_id)
    if request.method == "GET":
        try:
            return render_template("canvas_preview.html", canvas=database.get_canvas(canvas_id))
        except CanvasNotFoundError:
            return render_template("invalid_canvas.html")


@app.route("/canvas/<canvas_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_canvas(canvas_id):
    # okay so do i need a whole canvas profile model
    # bc what would even be in that
    # no right? there wouldnt be much if anything was needed there tbh bc like okay so maybe we could save last location but
    # then that means that we'd have to be transferring data about scrolling and stuff which tbh sounds like a really bad idea
    # okay so using visibility_change I can have it update current zoom/location and then save that in canvas profile
    # what else should go in the profile? i dont know tbh bc like thats kinda a lot of things to think of maybe i can
    if request.method == "GET":
        try:
            canvas = database.get_canvas(canvas_id)
            profile = get_user_canvas_profile(current_user, canvas)
            prep_canvas(canvas_id)
            return render_template("canvas_edit.html", canvas=canvas, profile=profile)
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
        database.create_canvas(form.id.data, current_user.id, form.max_paint.data, 4000, 4000, 10000, 5,
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
