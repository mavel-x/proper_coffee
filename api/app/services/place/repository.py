from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ObjectNotFoundError
from app.core.schemas import Location, Place, PlaceDB
from app.services.place.models import PlaceOrm


class ObjectAlreadyExists(Exception):
    pass


class PlaceRepository:
    model: type[PlaceOrm]

    def __init__(
        self,
        model: type[PlaceOrm],
        session: AsyncSession,
    ):
        self.model = model
        self.session = session

    async def add_one(self, place: Place) -> int:
        place_orm = self.model.from_schema(place)
        self.session.add(place_orm)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            if "Key (location)" in exc.args[0]:
                raise ObjectAlreadyExists("This location already exists") from exc
            raise exc
        return place_orm.id

    async def get_by_id(self, id_: int) -> PlaceDB:
        place_orm = (await self.session.scalars(select(self.model).where(self.model.id == id_))).first()
        if not place_orm:
            raise ObjectNotFoundError(f"Place with id {id_} not found")
        return place_orm.to_schema()

    async def get_nearest(self, user_location: Location, limit: int = 3) -> list[PlaceDB]:
        places_orm = await self.session.scalars(
            select(self.model)
            .order_by(self.model.location.distance_centroid(func.ST_GeomFromText(user_location.wkt)))
            .limit(limit)
        )
        return [place.to_schema() for place in places_orm]
