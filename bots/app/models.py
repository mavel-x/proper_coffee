from typing import Optional

from pydantic import BaseModel


class Place(BaseModel):
    name: str
    address: str
    distance: float
    description: Optional[str]
    photo_url: Optional[str]
    instagram_link: Optional[str]

    def create_bot_message(self) -> str:
        message = f"{self.name}\n\n"
        if self.description:
            message += (
               f"{self.description}\n"
               f"\n"
            )
        message += (
               f"{self.address}\n"
               f"{self.distance} km"
        )
        return message
