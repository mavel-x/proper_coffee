from typing import Optional

from geoalchemy2 import Geography, WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.schemas import Location, PlaceCreateGeocoded, PlaceDB


class PlaceOrm(DeclarativeBase):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[str]] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[str]] = mapped_column(
        TIMESTAMP,
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
    editor_verified: Mapped[bool] = mapped_column(default=False)
    user_verified: Mapped[bool] = mapped_column(default=False)

    @classmethod
    def from_schema(cls, place: PlaceCreateGeocoded) -> "PlaceOrm":
        place_dict = place.model_dump()
        place_dict["location"] = WKBElement(place.location.wkb, srid=4326)
        return cls(**place_dict)

    def to_schema(self) -> PlaceDB:
        place_dict = self.__dict__.copy()
        point = to_shape(self.location)
        place_dict["location"] = Location.from_point(point)
        return PlaceDB.model_validate(place_dict)


class CoffeeOrm(PlaceOrm):
    __tablename__ = "coffee"
