#!/usr/bin/python
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from prompts import generate_description
from models.property_types import (
    ResidentialListingData,
    LandListingData,
    OfficeSpaceListingData,
    CommercialListingData
)


app = FastAPI(
    title="Minite GPT3",
    description="Generates description for real estate listings from the listing parameters",
    version="2.0.0"
)


@app.get("/")
async def root():
    return "Hello World!!!"


@app.post('/residential_descriptions')
async def generate_apartment_description(residential_listing_data: ResidentialListingData, format: bool = False):
    """
    Generates descriptions for residential property types
    """
    return await generate_description(residential_listing_data, format=format)


@app.post('/land_descriptions')
async def land_description(land_listing_data: LandListingData, format: bool = False):
    """
    Generates descriptions for land property types
    """
    return await generate_description(land_listing_data, format=format)


@app.post('/office_space_descriptions')
async def office_space_description(office_space_data: OfficeSpaceListingData, format: bool = False):
    """
    Generates descriptions for office space property types
    """
    return await generate_description(office_space_data, format=format)


@app.post('/commercial_descriptions')
async def generate_land_description(commercial_listing_data: CommercialListingData, format: bool = False):
    """
    Generates descriptions for commercial property types
    """
    return await generate_description(commercial_listing_data, format=format)


@app.get('/access_logs')
async def get_gunicorn_access_logs():
    path = os.path.join(os.getcwd(), 'gunicorn-access.log')
    log_path = os.environ.get("ACCESS_LOGFILE", path)
    data = ""
    try:
        with open(log_path, 'r') as f:
            data += "<ul>"
            for s in f.readlines():
                data += "<li>" + str(s) + "</li>"
            data += "</ul>"

    except:
        pass
    return HTMLResponse(content=data)

@app.get('/error_logs')
async def get_gunicorn_error_logs():
    path = os.path.join(os.getcwd(), 'gunicorn-error.log')
    log_path = os.environ.get("ERROR_LOGFILE", path)
    data = ""
    try:
        with open(log_path, 'r') as f:
            data += "<ul>"
            for s in f.readlines():
                data += "<li>" + str(s) + "</li>"
            data += "</ul>"
    except:
        pass
    return HTMLResponse(content=data)
