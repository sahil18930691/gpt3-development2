#!/usr/bin/python
from fastapi import FastAPI, HTTPException

from prompts import generate_description
from models.property_types import (
    ApartmentListingData,
    BuilderFloorListingData,
    LandListingData,
    OfficeSpaceListingData,
    PlotListingData
)


app = FastAPI()


@app.get("/")
async def root():
    return "Hello World"


@app.post('/apartment_descriptions')
async def generate_apartment_description(apartment_listing_data: ApartmentListingData):
    """
    Generates descriptions for properties of type Apartment
    """
    return generate_description(apartment_listing_data)


@app.post('/builder_floor_descriptions')
async def generate_builder_floor_description(builder_floor_listing_data: BuilderFloorListingData):
    """
    Generates descriptions for properties of type Builder Floor
    """
    return dict(builder_floor_listing_data)


@app.post('/land_descriptions')
async def generate_apartment_description(land_listing_data: LandListingData):
    """
    Generates descriptions for properties of type Land
    """
    return generate_description(land_listing_data)


@app.post('/office_space_descriptions')
async def generate_apartment_description(office_space_listing_data: OfficeSpaceListingData):
    """
    Generates descriptions for properties of type Office Space
    """
    return generate_description(office_space_listing_data)


@app.post('/plot_descriptions')
async def generate_apartment_description(plot_listing_data: PlotListingData):
    """
    Generates descriptions for properties of type Plot
    """
    return generate_description(plot_listing_data)

