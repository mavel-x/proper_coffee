from typing import Optional

from pydantic import BaseModel, ConfigDict
from shapely import Point


class Location(BaseModel):
    latitude: float
    longitude: float

    @classmethod
    def from_point(cls, point: Point) -> "Location":
        return cls(latitude=point.y, longitude=point.x)


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


class PlaceCreateGeocoded(PlaceCreate):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    location: Point


class Place(PlaceCreate):
    location: Location


class PlaceWithDistance(Place):
    distance_km: float


class PlaceDB(Place):
    id: int
