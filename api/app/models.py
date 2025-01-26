from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.schemas.location import Location, LocationDB
from app.schemas.place import PlaceDB, PlaceDBCreate


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def from_create_schema(cls, instance: BaseModel) -> "Base":
        raise NotImplementedError

    def to_db_schema(self) -> "BaseModel":
        raise NotImplementedError


class LocationOrm(Base):
    __tablename__ = "location"

    latitude: Mapped[Decimal]
    longitude: Mapped[Decimal]
    place: Mapped["PlaceOrm"] = relationship(back_populates="location")

    @classmethod
    def from_create_schema(cls, location: Location) -> "LocationOrm":
        return cls(**location.model_dump())

    def to_db_schema(self) -> LocationDB:
        return LocationDB.model_validate(self.__dict__)


class PlaceOrm(Base):
    __tablename__ = "place"

    name: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(default="")
    photo_url: Mapped[Optional[str]] = mapped_column(default="")
    instagram_link: Mapped[Optional[str]] = mapped_column(default="")
    address: Mapped[str]
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id", ondelete="CASCADE"))
    location: Mapped["LocationOrm"] = relationship(back_populates="place")

    @classmethod
    def from_create_schema(cls, place: PlaceDBCreate) -> "PlaceOrm":
        place_dict = place.model_dump()
        place_dict.pop("location")
        place_dict["location_id"] = place.location.id
        return cls(**place_dict)

    def to_db_schema(self) -> PlaceDB:
        place_dict = self.__dict__
        place_dict.update({"location": LocationDB.model_validate(self.location.__dict__)})
        return PlaceDB.model_validate(place_dict)
