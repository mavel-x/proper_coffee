from _decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.schemata.location import LocationDB, Location


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
