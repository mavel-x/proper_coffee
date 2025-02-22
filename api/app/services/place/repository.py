from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ObjectNotFoundError
from app.core.schemas import Place, PlaceDB
from app.services.place.models import PlaceOrm


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
        place_orm = self.model.from_create_schema(place)
        self.session.add(place_orm)
        await self.session.commit()
        return place_orm.id

    async def get_by_id(self, id_: int) -> PlaceDB:
        place: PlaceOrm = (await self.session.scalars(select(self.model).where(self.model.id == id_))).first()
        if not place:
            raise ObjectNotFoundError(f"Place with id {id_} not found")
        return place.to_db_schema()
