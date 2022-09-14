from models import db, Canvas
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from exc import CanvasNotFoundError, DatabaseConfigurationError


def create_canvas(canvas_id, owner, max_paint, width, height, paint_recharge_amount, paint_recharge_time,
                  allow_anonymous, access_type):
    new_canvas = Canvas(id=canvas_id, owner=owner, max_paint=max_paint, width=width, height=height,
                        paint_recharge_amount=paint_recharge_amount, paint_recharge_time=paint_recharge_time,
                        allow_anonymous=allow_anonymous, access=access_type)
    db.session.add(new_canvas)
    db.session.commit()


def get_canvas(canvas_id):
    try:
        canvas = db.session.query(Canvas).filter_by(id=canvas_id).first()
        if canvas is None:
            raise CanvasNotFoundError(f"No canvas with id {canvas_id} could be found")
        else:
            return canvas
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


def init_db():
    db.create_all()
