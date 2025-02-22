import httpx
import pytest
import pytest_asyncio
from app.core.exceptions import AddressNotFoundError
from app.services.geocoding import GeocodingService
from httpx import Response
from shapely.geometry.point import Point


@pytest_asyncio.fixture()
async def geocoder():
    async with httpx.AsyncClient() as http_client:
        yield GeocodingService(api_key="test-key", http_client=http_client)


@pytest.mark.asyncio
async def test_location_in_from_address(respx_mock, geocoder: GeocodingService):
    address = "Müllerstraße 28, 13353 Berlin"
    mock_features = {
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "lon": 13.3580691,
                    "lat": 52.5472567,
                },
            }
        ]
    }
    mock_endpoint = respx_mock.get(
        "https://api.geoapify.com/v1/geocode/search?text=M%C3%BCllerstra%C3%9Fe+28%2C+13353+Berlin&apiKey=test-key"
    ).respond(status_code=200, json=mock_features)
    expected = Point(13.3580691, 52.5472567)
    actual = await geocoder.geocode(address)
    assert actual == expected
    assert mock_endpoint.call_count == 1


@pytest.mark.asyncio
async def test_location_in_from_address_invalid(respx_mock, geocoder: GeocodingService):
    address = "wo;efuner;gjewrgpowefmiwe"
    mock_features = {"features": []}
    respx_mock.get("https://api.geoapify.com/v1/geocode/search?text=wo;efuner;gjewrgpowefmiwe&apiKey=test-key").mock(
        return_value=Response(status_code=200, json=mock_features)
    )
    with pytest.raises(AddressNotFoundError):
        await geocoder.geocode(address)
