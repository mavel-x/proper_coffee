from decimal import Decimal
from typing import Optional

import requests
from sqlmodel import SQLModel, Field, Relationship


class LocationBase(SQLModel):
    latitude: Decimal
    longitude: Decimal


class Location(LocationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    place: Optional['Place'] = Relationship(back_populates='location')


class LocationRead(LocationBase):
    id: int


class LocationIn(LocationBase):
    @classmethod
    def from_address(cls, address: str, api_key: str) -> 'LocationIn':
        url = 'https://api.geoapify.com/v1/geocode/search'
        params = {
            'text': address,
            'apiKey': api_key,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        features = response.json()['features']
        if not features:
            raise ValueError(f'Unable to geocode address: {address}')
        properties = features[0]['properties']
        return cls(latitude=properties['lat'], longitude=properties['lon'])


class LocationReadWithDistance(LocationRead):
    distance: Decimal


class PlaceBase(SQLModel):
    name: str
    description = Field(default='')
    photo_url = Field(default='')
    instagram_link = Field(default='')
    address: str


class Place(PlaceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.id")
    location: Location = Relationship(back_populates='place')


class PlaceRead(PlaceBase):
    id: int


class PlaceReadWithLocation(PlaceRead):
    location: Optional[LocationBase]


class PlaceReadWithDistance(PlaceRead):
    distance: Decimal


class PlaceCreate(PlaceBase):
    pass
