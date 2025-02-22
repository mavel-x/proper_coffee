from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer
from shapely import Point


class Location(BaseModel):
    latitude: float
    longitude: float


class PlaceCreatedResponse(BaseModel):
    id: int


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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    location: Point

    @field_serializer("location")
    def serialize_location(self, value: Point) -> str:
        return f"{value.y}, {value.x}"


class PlaceWithDistance(Place):
    distance_km: float


class PlaceDB(Place):
    id: int
