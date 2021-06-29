#!/usr/bin/python
from fastapi import FastAPI, HTTPException

from prompts import generate_description
from models.property_types import (
    ApartmentListingData,
    BuilderFloorListingData,
    LandListingData,
    OfficeSpaceListingData,
    PlotListingData,
    VillaListingData,
    PenthouseListingData,
    IndependentHouseListingData
)


app = FastAPI()


@app.get("/")
async def root():
    return "Hello World"


@app.post('/apartment_descriptions')
async def generate_apartment_description(apartment_listing_data: ApartmentListingData, format: bool = False):
    """
    Generates descriptions for properties of type Apartment
    """
    return generate_description(apartment_listing_data, format=format)


@app.post('/builder_floor_descriptions')
async def generate_builder_floor_description(builder_floor_listing_data: BuilderFloorListingData, format: bool = False):
    """
    Generates descriptions for properties of type Builder Floor
    """
    return generate_description(builder_floor_listing_data, format=format)


@app.post('/land_descriptions')
async def generate_land_description(land_listing_data: LandListingData, format: bool = False):
    """
    Generates descriptions for properties of type Land
    """
    return generate_description(land_listing_data, format=format)


@app.post('/office_space_descriptions')
async def generate_office_space_description(office_space_listing_data: OfficeSpaceListingData, format: bool = False):
    """
    Generates descriptions for properties of type Office Space
    """
    return generate_description(office_space_listing_data, format=format)


@app.post('/plot_descriptions')
async def generate_plot_description(plot_listing_data: PlotListingData, format: bool = False):
    """
    Generates descriptions for properties of type Plot
    """
    return generate_description(plot_listing_data, format=format)

@app.post('/villa_descriptions')
async def generate_villa_description(villa_listing_data: VillaListingData, format: bool = False):
    """
    Generates descriptions for properties of type Plot
    """
    return generate_description(villa_listing_data, format=format)

@app.post('/penthouse_descriptions')
async def generate_penthouse_description(penthouse_listing_data: PenthouseListingData, format: bool = False):
    """
    Generates descriptions for properties of type Plot
    """
    return generate_description(penthouse_listing_data, format=format)

@app.post('/independent_house_descriptions')
async def generate_independent_house_description(independent_house_listing_data: IndependentHouseListingData, format: bool = False):
    """
    Generates descriptions for properties of type Plot
    """
    return generate_description(independent_house_listing_data, format=format)

