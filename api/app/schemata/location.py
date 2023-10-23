from _decimal import Decimal

from pydantic import BaseModel


class Location(BaseModel):
    latitude: Decimal
    longitude: Decimal


class LocationDB(Location):
    id: int
