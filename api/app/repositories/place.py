from app.models import PlaceOrm
from . import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    model = PlaceOrm
