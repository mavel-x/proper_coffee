from typing import Optional

from pydantic import BaseModel


class Location(BaseModel):
    latitude: float
    longitude: float


class Place(BaseModel):
    name: str
    address: str
    location: Location
    distance_km: float
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    ig_url: Optional[str] = ""
    website_url: Optional[str] = ""
    editor_verified: Optional[bool] = False
    user_verified: Optional[bool] = False

    def create_bot_message(self) -> str:
        message = f"{self.name}\n"
        if self.ig_url:
            message += f"{self.ig_url}\n" f"\n"
        if self.description:
            message += f"{self.description}\n" f"\n"
        message += f"{self.address}\n" f"{self.distance_km:.3g} km away"
        return message
