from typing import Optional

from pydantic import BaseModel
from shapely.geometry import Point


class Place(BaseModel):
    name: str
    address: str
    location: Point
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    ig_url: Optional[str] = ""
    website_url: Optional[str] = ""
    verified: Optional[bool] = False
