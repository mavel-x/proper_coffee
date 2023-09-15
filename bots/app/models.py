from typing import Optional

from pydantic import BaseModel


class Location(BaseModel):
    latitude: float
    longitude: float


class Place(BaseModel):
    name: str
    address: str
    distance: float
    description: Optional[str]
    photo_url: Optional[str]
    instagram_link: Optional[str]
    location: Location

    def create_bot_message(self) -> str:
        message = f"{self.name}\n"
        if self.instagram_link:
            message += (
                f"{self.instagram_link}\n"
                f"\n"
            )
        if self.description:
            message += (
               f"{self.description}\n"
               f"\n"
            )
        message += (
               f"{self.address}\n"
               f"{self.distance} km away"
        )
        return message
