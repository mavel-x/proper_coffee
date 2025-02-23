from typing import Optional

from geopy import Point
from pydantic import BaseModel


class Location(BaseModel):
    latitude: float
    longitude: float

    def to_point(self) -> Point:
        return Point(
            latitude=self.latitude,
            longitude=self.longitude,
        )

    @property
    def wkt(self) -> str:
        return f"POINT ({self.longitude} {self.latitude})"


class CreatedResponse(BaseModel):
    id: int


class DetailResponse(BaseModel):
    detail: str


class PlaceCreate(BaseModel):
    name: str
    address: str
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    ig_url: Optional[str] = ""
    website_url: Optional[str] = ""
    editor_verified: Optional[bool] = False
    user_verified: Optional[bool] = False


class Place(PlaceCreate):
    location: Location


class PlaceWithDistance(Place):
    distance_km: float


class PlaceDB(Place):
    id: int
