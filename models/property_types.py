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


class PenthouseListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'penthouse'
    furnishing: str
    bedrooms: int
    bathrooms: int
    parking: Optional[int]
    property_age: str
    floor_number: int
    total_floor_count: int


class VillaListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'villa'
    area_type: Optional[str]
    furnishing: str
    bedrooms: int
    bathrooms: int
    parking: Optional[int]
    property_age: str
    total_floor_count: int


class IndependentHouseListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'independent_house'
    area_type: Optional[str]
    furnishing: str
    bedrooms: int
    bathrooms: int
    parking: Optional[int]
    property_age: str
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


class IndustrialPlotListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'industrial_plot'
    plot_number: int


class OfficeSpaceInItSezListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'office_space_in_it_sez'
    office_space_type: str
    pantry: str
    furnishing: str
    washroom_present: str
    parking: Optional[int]
    floor_number: int
    total_floor_count: int

class ShopListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'shop'
    furnishing: str
    washroom_present: str
    parking: Optional[int]
    floor_number: int

class ShowroomListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'showroom'
    furnishing: str
    washroom_present: str
    parking: Optional[int]
    floor_number: int

class WarehouseListingData(BaseListingData):
    property_type: Optional[PropertyType] = 'warehouse'
    washroom_present: str
    parking: int
