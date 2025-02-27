from urllib.parse import urljoin

import httpx

from app.schemas import Place


class PlacesClient:
    def __init__(self, api_url: str, http_client: httpx.AsyncClient):
        self._nearest_url = urljoin(api_url, "nearest")
        self._http_client = http_client

    async def get_nearest_places(self, latitude: float, longitude: float):
        params = {"latitude": latitude, "longitude": longitude}
        response = await self._http_client.get(self._nearest_url, params=params)
        response.raise_for_status()
        return [Place(**loc) for loc in response.json()]
