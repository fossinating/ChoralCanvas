from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from exc import *

from database import db_session, init_db
from models import *


def init():
    init_db()


def create_canvas(canvas_id, owner, max_paint, paint_regen, allow_anonymous, access_type):
    new_canvas = Canvas(id=canvas_id, owner=owner, max_paint=max_paint, paint_regen=paint_regen,
                        allow_anonymous=allow_anonymous, access=access_type)
    db_session.add(new_canvas)
    db_session.commit()


def get_canvas(canvas_id):
    try:
        return db_session.query(Canvas).filter_by(id=canvas_id).one()
    except NoResultFound:
        raise CanvasNotFoundError(f"No canvas with id {canvas_id} could be found")
    except MultipleResultsFound:
        raise DatabaseConfigurationError(f"Multiple canvas entries for id {canvas_id} were found")


def canvas_exists(canvas_id):
    try:
        get_canvas(canvas_id)
        return True
    except CanvasNotFoundError:
        return False
    except DatabaseConfigurationError:
        raise DatabaseConfigurationError(f"Multiple canvas entries for id {canvas_id} were found")
