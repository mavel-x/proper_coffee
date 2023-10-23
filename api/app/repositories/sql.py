from typing import Sequence

from pydantic import BaseModel
from sqlalchemy import update, select
from sqlalchemy.orm import Session

from app.models import Base
from app.repositories import AbstractRepository


class SQLAlchemyRepository(AbstractRepository):
    model: Base = None

    def __init__(self, session: Session):
        self.session = session

    def add_one(self, obj: BaseModel) -> int:
        instance = self.model.from_create_schema(obj)
        self.session.add(instance)
        self.session.flush()
        return instance.id

    def add_all(self, objects: Sequence[BaseModel]) -> None:
        instances = [self.model.from_create_schema(obj) for obj in objects]
        self.session.add_all(instances)
        self.session.flush()

    def edit_one(self, pk: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=pk).returning(self.model.id)
        res = self.session.execute(stmt)
        return res.scalar_one()

    def get_by_id(self, pk: int) -> BaseModel | None:
        stmt = select(self.model).filter_by(id=pk)
        res = self.session.execute(stmt)
        res = res.scalar_one_or_none()
        if res:
            return res.to_db_schema()
        return res

    def get_all(self, **filter_by) -> list[BaseModel]:
        stmt = select(self.model).filter_by(**filter_by)
        res = self.session.execute(stmt)
        res = [row[0].to_db_schema() for row in res.all()]
        return res

    def filter_in(self, field_name: str, values: Sequence) -> list[BaseModel]:
        field = getattr(self.model, field_name)
        stmt = select(self.model).filter(field.in_(values))
        res = self.session.execute(stmt)
        return [row[0].to_db_schema() for row in res.all()]

    def get_or_create(self, obj: BaseModel) -> BaseModel:
        instance = self.session.query(self.model).filter_by(**obj.model_dump()).first()
        if not instance:
            instance = self.model.from_create_schema(obj)
            self.session.add(instance)
            self.session.flush()
        return instance.to_db_schema()
