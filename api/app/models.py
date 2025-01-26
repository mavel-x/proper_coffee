from typing import Optional

from geoalchemy2 import Geography, WKBElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.schemas.place import PlaceDB, PlaceDBCreate


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def from_create_schema(cls, instance: BaseModel) -> "Base":
        raise NotImplementedError

    def to_db_schema(self) -> "BaseModel":
        raise NotImplementedError


class PlaceOrm(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[str]] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[str]] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[Optional[str]] = mapped_column(nullable=False)
    location: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
        unique=True,
    )
    description: Mapped[Optional[str]] = mapped_column(default="")
    image_url: Mapped[Optional[str]] = mapped_column(default="")
    ig_url: Mapped[Optional[str]] = mapped_column(default="")
    website_url: Mapped[Optional[str]] = mapped_column(default="")
    verified: Mapped[bool] = mapped_column(default=False)

    @classmethod
    def from_create_schema(cls, place: PlaceDBCreate) -> "PlaceOrm":
        place_dict = place.model_dump()
        lat = place_dict.pop("latitude")
        lon = place_dict.pop("longitude")
        place_dict["location"] = f"SRID=4326;POINT({lon} {lat})"
        return cls(**place_dict)

    def to_db_schema(self) -> PlaceDB:
        point = to_shape(self.location)  # Converts to Shapely Point
        lat, lon = point.y, point.x

        place_dict = self.__dict__.copy()
        place_dict["latitude"] = lat
        place_dict["longitude"] = lon

        return PlaceDB.model_validate(place_dict)
