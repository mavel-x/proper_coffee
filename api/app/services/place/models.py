from typing import Optional

from geoalchemy2 import Geography, WKTElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.schemas import Place, PlaceDB


class Base(DeclarativeBase):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}

    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def from_create_schema(cls, instance: BaseModel) -> "Base":
        raise NotImplementedError

    def to_db_schema(self) -> "BaseModel":
        raise NotImplementedError


class PlaceOrm(Base):
    __abstract__ = True

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
    location: Mapped[Geography] = mapped_column(
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
    def from_create_schema(cls, place: Place) -> "PlaceOrm":
        place_dict = place.model_dump()
        place_dict["location"] = WKTElement(place.location.wkt, srid=4326)
        return cls(**place_dict)

    def to_db_schema(self) -> PlaceDB:
        place_dict = self.__dict__.copy()
        place_dict["location"] = to_shape(self.location)
        return PlaceDB.model_validate(place_dict)


class CoffeeOrm(PlaceOrm):
    __tablename__ = "coffee"
