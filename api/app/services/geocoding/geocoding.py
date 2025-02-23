import httpx

from app.core.exceptions import AddressNotFoundError, GeocoderUnavailableError
from app.core.schemas import Location


class GeocodingService:
    api_url = "https://api.geoapify.com/v1/geocode/search"

    def __init__(self, api_key, http_client: httpx.AsyncClient):
        self._api_key = api_key
        self._http_client = http_client

    async def geocode(self, address) -> Location:
        params = {
            "text": address,
            "apiKey": self._api_key,
        }
        try:
            response = await self._http_client.get(self.api_url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GeocoderUnavailableError from exc

        features = response.json()["features"]
        if not features:
            raise AddressNotFoundError(f"Unable to geocode address: {address}")

        properties = features[0]["properties"]
        return Location(
            latitude=properties["lat"],
            longitude=properties["lon"],
        )
