from typing import Optional

from _decimal import Decimal
from pydantic import BaseModel

from app.schemas.location import Location, LocationDB


class Place(BaseModel):
    name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    instagram_link: Optional[str] = None
    address: str


class PlaceDBCreate(Place):
    location: LocationDB


class PlaceDB(Place):
    id: int
    location: LocationDB


class PlaceWithLocation(Place):
    location: Location


class PlaceWithDistance(PlaceWithLocation):
    distance: Decimal
