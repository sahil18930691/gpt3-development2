#!usr/bin/python
import os
import json
from enum import Enum
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prompts import create_prompt

app = FastAPI()


BASE_PAYLOAD = {
    "max_tokens": 150,
    "temperature": 0.5,
    "top_p": 0.8,
    "n": 1,
    "stream": False,
    "logprobs": None,
    "stop": ["-----"]
}

API_KEY = os.getenv('API_KEY')
MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


class PropertyType(str, Enum):
    builder_floor = 'builder_floor'
    apartment = 'apartment'
    plot = 'plot'
    land = 'land'
    office_space = 'office_space'


class ListingType(str, Enum):
    sale = 'sale'
    rent = 'rent'


class ListingData(BaseModel):
    property_type: PropertyType
    keywords: str
    listing_type: ListingType
    project: str
    block: str
    locality: str
    city: str
    furnishing: str
    price: int
    bedrooms: int
    bathrooms: int
    parking: Optional[int]
    area: int
    area_unit: str
    facing: str
    property_age: str
    floor_number: int
    total_floor_count: int
    amenities: str



@app.get("/")
async def root():
    return "Hello World"


@app.get('/descriptions')
async def generate_listing_description(listing_data: ListingData):
    """
    Generates property descriptions for the given listing data in request body
    """
    payload = dict(BASE_PAYLOAD)
    payload['prompt'] = create_prompt(listing_data)
    
    try:
        response = requests.post(MODEL_ENDPOINT, headers=headers, data=json.dumps(payload))
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request to remote server failed: {str(e)}")
    
    print(data)
    description = data['choices'][0]['text'].strip()
    return description

