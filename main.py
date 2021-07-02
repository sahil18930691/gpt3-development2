#!/usr/bin/python
from fastapi import FastAPI, HTTPException

from prompts import generate_description
from models.property_types import (
    ResidentialListingData,
    LandListingData,
    OfficeSpaceListingData,
    CommercialListingData
)

app = FastAPI()


@app.get("/")
async def root():
    return "Hello World"


@app.post('/residential_descriptions')
async def generate_apartment_description(residential_listing_data: ResidentialListingData, format: bool = False):
    """
    Generates descriptions for residential property types
    """
    return generate_description(residential_listing_data, format=format)


@app.post('/land_descriptions')
async def land_description(land_listing_data: LandListingData, format: bool = False):
    """
    Generates descriptions for land property types
    """
    return generate_description(land_listing_data, format=format)


@app.post('/office_space_descriptions')
async def office_space_description(office_space_data: OfficeSpaceListingData, format: bool = False):
    """
    Generates descriptions for office space property types
    """
    return generate_description(office_space_data, format=format)


@app.post('/commercial_descriptions')
async def generate_land_description(commercial_listing_data: CommercialListingData, format: bool = False):
    """
    Generates descriptions for commercial property types
    """
    return generate_description(commercial_listing_data, format=format)
