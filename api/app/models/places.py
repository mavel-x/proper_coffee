from decimal import Decimal
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class LocationBase(SQLModel):
    latitude: Decimal
    longitude: Decimal


class Location(LocationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    place: Optional['Place'] = Relationship(back_populates='location')


class LocationIn(LocationBase):
    pass


class PlaceBase(SQLModel):
    name: str
    description = Field(default='')
    photo_url = Field(default='')
    instagram_link = Field(default='')
    address: str


class Place(PlaceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.id")
    location: Location = Relationship(back_populates='place')


class PlaceRead(PlaceBase):
    id: int


class PlaceReadWithLocation(PlaceRead):
    location: Optional[LocationBase]


class PlaceReadWithDistance(PlaceReadWithLocation):
    distance: Decimal


class PlaceCreate(PlaceBase):
    pass
