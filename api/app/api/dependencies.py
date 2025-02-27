from fastapi import Request

from app.core.database import DatabaseSessionManager
from app.env_settings import Settings
from app.services.geocoding import GeocodingService
from app.services.place.models import CoffeeOrm
from app.services.place.repository import PlaceRepository


async def get_geocoding_service(request: Request) -> GeocodingService:
    settings: Settings = request.app.state.settings
    yield GeocodingService(
        api_key=settings.geoapify_api_key,
        http_client=request.app.state.http_client,
    )


async def get_coffee_repo(request: Request) -> PlaceRepository:
    session_manager: DatabaseSessionManager = request.app.state.session_manager
    async with session_manager.session() as session:
        yield PlaceRepository(CoffeeOrm, session)
