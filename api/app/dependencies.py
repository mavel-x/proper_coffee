from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.services.geocoding import Geocoder
from app.settings import Settings


class SessionDropIn:
    pass


@lru_cache()
def get_settings():
    return Settings()


def get_geocoder(settings: Annotated[Settings, Depends(get_settings)]) -> Geocoder:
    return Geocoder(settings.geo_api)
