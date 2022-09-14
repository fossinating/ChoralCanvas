from flask_wtf import FlaskForm
from wtforms import BooleanField, validators, StringField, ValidationError, IntegerField

from database import canvas_exists


class CanvasCreationForm(FlaskForm):
    id = StringField("Canvas ID", validators=[validators.InputRequired(message="Must include a canvas")])
    max_paint = IntegerField("Maximum Paint",
                             validators=[validators.InputRequired(message="Required"),
                                         validators.NumberRange(min=1, max=1000000, message=
                                         "Max paint amount must be between %(min)s and %(max)s")])
    paint_regen = IntegerField("Paint Regen Rate",
                               validators=[validators.InputRequired(message="Required"),
                                           validators.NumberRange(min=1, max=100000, message=
                                           "Paint regen rate must be between %(min)s and %(max)s")])
    allow_anonymous = BooleanField("Allow Anonymous Painting")

    def validate_id(form, field):
        print("testing")
        if len(field.data) > 12:
            print("fail")
            raise ValidationError("Canvas ID cannot be more than 12 characters")
        if not field.data.isalpha():
            print("fail")
            raise ValidationError("Canvas ID must be made up of only characters from a-z")
        if canvas_exists(field.data):
            print(field.data)
            print("fail")
            raise ValidationError("This canvas ID is already taken")
        print("nothing failed for id")
