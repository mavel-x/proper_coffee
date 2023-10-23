from app.models import LocationOrm
from . import SQLAlchemyRepository


class LocationRepository(SQLAlchemyRepository):
    model = LocationOrm
