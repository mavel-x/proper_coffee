import httpx

from .exceptions import GeocodingError


class Geocoder:
    api_url = 'https://api.geoapify.com/v1/geocode/search'

    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address) -> dict[str, float]:
        params = {
            'text': address,
            'apiKey': self.api_key,
        }
        response = httpx.get(self.api_url, params=params)
        response.raise_for_status()
        features = response.json()['features']
        if not features:
            raise GeocodingError(f'Unable to geocode address: {address}')
        properties = features[0]['properties']
        return {
            'latitude': properties['lat'],
            'longitude': properties['lon'],
        }
