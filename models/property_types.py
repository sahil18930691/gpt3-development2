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
    penthouse = 'penthouse'
    villa = 'villa'
    independent_house = 'independent_house'
    industrial_plot = 'industrial_plot'
    office_space_in_it_sez = 'office_space_in_it_sez'
    shop = 'shop'
    showroom = 'showroom'
    warehouse = 'warehouse'


class ListingType(str, Enum):
    sale = 'sale'
    rent = 'rent'


class ResidentialPropertyType(str, Enum):
    apartment = 'apartment'
    builder_floor = 'builder_floor'
    penthouse = 'penthouse'
    villa = 'villa'
    independent_house = 'independent_house'


class OfficeSpacePropertyType(str, Enum):
    office_space = 'office_space'
    office_space_sez = 'office_space_sez'


class CommercialPropertyType(str, Enum):
    shop = 'shop'
    showroom = 'showroom'
    warehouse = 'warehouse'


class LandPropertyType(str, Enum):
    land = 'land'
    industrial_plot = 'industrial_plot'
    plot = 'plot'


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


class ResidentialListingData(BaseListingData):
    property_type: ResidentialPropertyType
    furnishing: str
    project: Optional[str]
    tower: Optional[str]
    bedrooms: int
    bathrooms: int
    parking: int
    property_age: Optional[str]
    floor_number: Optional[int]
    total_floor_count: Optional[int]


class LandListingData(BaseListingData):
    property_type: LandPropertyType
    land_number: Optional[int]
    plot_number: int


class OfficeSpaceListingData(BaseListingData):
    property_type: OfficeSpacePropertyType
    office_space_type: str
    pantry: str
    furnishing: str
    washroom_present: str
    parking: Optional[int]
    floor_number: int
    total_floor_count: int


class CommercialListingData(BaseListingData):
    property_type: CommercialPropertyType
    furnishing: Optional[str]
    washroom_present: str
    parking: Optional[int]
    floor_number: Optional[int]
