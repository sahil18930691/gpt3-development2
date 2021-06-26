#!/usr/bin/python
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PropertyType(str, Enum):
    apartment = 'apartment'
    builder_floor = 'builder_floor'
    land = 'land'
    office_space = 'office_space'
    plot = 'plot'


class ListingType(str, Enum):
    sale = 'sale'
    rent = 'rent'


class BaseListingData(BaseModel):
    property_type: PropertyType
    listing_type: ListingType
    keywords: str
    locality: str
    city: str
    price: int
    area: int
    area_unit: str
    facing: str
    amenities: str


class ApartmentListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'apartment'
    furnishing: str
    bedrooms: int
    bathrooms: int
    parking: Optional[int]
    property_age: str
    floor_number: int
    total_floor_count: int


class BuilderFloorListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'builder_floor'
    project: str
    tower: str
    furnishing: str
    bedrooms: int
    bathrooms: int
    parking: Optional[int]
    property_age: str
    floor_number: int
    total_floor_count: int


class LandListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'land'
    land_number: int


class OfficeSpaceListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'office_space'
    office_space_type: str
    pantry: str
    furnishing: str
    washroom_present: str
    parking: int
    floor_number: int
    total_floor_count: int


class PlotListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'plot'
    plot_number: int
