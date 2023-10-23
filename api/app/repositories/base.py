from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence

from pydantic import BaseModel


class AbstractRepository(ABC):
    @abstractmethod
    def add_one(self, obj: BaseModel) -> int:
        raise NotImplementedError

    def add_all(self, objects: Sequence[BaseModel]) -> int:
        raise NotImplementedError

    def edit_one(self, pk: int, obj: dict) -> int:
        raise NotImplementedError

    def get_by_id(self, pk: int) -> BaseModel:
        raise NotImplementedError

    def get_all(self, **filter_by) -> list[BaseModel]:
        raise NotImplementedError

    def filter_in(self, field_name: str, values: Sequence) -> list[BaseModel]:
        raise NotImplementedError

    def get_or_create(self, obj: BaseModel) -> BaseModel:
        raise NotImplementedError
