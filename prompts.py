#!/usr/bin/python
import os
import json
import requests
from babel.numbers import format_currency
from fastapi import HTTPException


API_KEY = os.getenv('API_KEY')
MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT')



BASE_PAYLOAD = {
    "max_tokens": 150,
    "temperature": 0.5,
    "top_p": 0.8,
    "n": 1,
    "stream": False,
    "logprobs": None,
    "stop": ["-----"]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def generate_description(listing_data, format=False):
    """
    Generates a description for any type of BaseListingData
    """
    payload = dict(BASE_PAYLOAD)
    payload['prompt'] = create_prompt(listing_data)
    
    try:
        response = requests.post(MODEL_ENDPOINT, headers=headers, data=json.dumps(payload))
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request to remote server failed: {str(e)}")
    
    description = data['choices'][0]['text'].strip()
    
    if format:
        description = format_description(description)

    return description


def get_examples(property_type, listing_type):
    """
    Get all the examples from the JSON file for the specified
    property_type and listing_type
    """
    if os.path.isfile(f'prompts/{property_type}.json'):
        json_path = f'prompts/{property_type}.json'
    elif os.path.isfile(f'prompts/{property_type}_{listing_type}.json'):
        json_path = f'prompts/{property_type}_{listing_type}.json'
    else:
        raise HTTPException(
            status_code=400,
            detail="Listing of {listing_type} with {property_type} is not supported"
        )
    with open(json_path, 'rb') as json_file:
        examples = json.loads(json_file.read())
    return examples


def format_listing_data(listing_data):
    """
    Formats the examples for usage in the prompt
    """
    prompt_string = ""
    if 'listing_type' in listing_data:
        prompt_string += f"Listing type: {listing_data['listing_type']}\n"

    if 'keywords' in listing_data:
        prompt_string += f"Keywords: {listing_data['keywords']}\n"

    if "tower" in listing_data:
        prompt_string += f"Tower: {listing_data['tower']}\n"
    
    if "project" in listing_data:
        prompt_string += f"Project: {listing_data['project']}\n"

    if "locality" in listing_data:
        prompt_string += f"Locality: {listing_data['locality']}\n"

    if "city" in listing_data:
        prompt_string += f"City: {listing_data['city']}\n"

    if "furnishing" in listing_data:
        prompt_string += f"Furnishing: {listing_data['furnishing']}\n"
    
    if "office_space_type" in listing_data:
        prompt_string += f"Office fitting: {listing_data['office_space_type']}\n"

    if "bedrooms" in listing_data:
        prompt_string += f"Bedrooms: {listing_data['bedrooms']}\n"

    if "bathrooms" in listing_data:
        prompt_string += f"Bathrooms: {listing_data['bathrooms']}\n"
    
    if "pantry" in listing_data:
        prompt_string += f"Pantry: {listing_data['pantry']}\n"
    
    if "washroom_present" in listing_data:
        prompt_string += f"Washroom Present: {listing_data['washroom_present']}\n"

    if "parking" in listing_data:
        prompt_string += f"Parking: {listing_data['parking']}\n"
    
    if "price" in listing_data:
        formatted_price = format_currency(listing_data['price'], 'INR', locale='en_IN')[1:].split('.')[0]
        prompt_string += f"Price: {formatted_price}\n"
    
    # Concatenate area and area_unit and remove full stops, if any
    if "area" in listing_data:
        prompt_string += f"Area: {listing_data['area']} {listing_data['area_unit'].replace('.', '')}\n"
    
    if "facing" in listing_data:
        prompt_string += f"Facing: {listing_data['facing']}\n"
    
    if "property_age" in listing_data:
        prompt_string += f"Property Age: {listing_data['property_age']}\n"
    
    if "plot_number" in listing_data:
        prompt_string += f"Plot Number: {listing_data['plot_number']}\n"
    
    if "floor_number" in listing_data:
        prompt_string += f"Floor number: {listing_data['floor_number']}\n"
    
    if "total_floor_count" in listing_data:
        prompt_string += f"Total Floor Count: {listing_data['total_floor_count']}\n"

    if "amenities" in listing_data:
        prompt_string += f"Amenities: {listing_data['amenities']}\n"

    if "description" in listing_data:
        prompt_string += f"Description: {listing_data['description']}\n"

    return prompt_string


def create_prompt(listing_form_data):
    """
    Creates the prompt for a given listing data by adding examples followed by incoming
    data
    """
    listing_data = dict(listing_form_data)
    examples = get_examples(listing_data['property_type'], listing_data['listing_type'])
    prompt_string = ""
    for example in examples:
        prompt_string += format_listing_data(example)
        prompt_string += "\n\n-----\n\n"

    prompt_string += format_listing_data(listing_data)
    prompt_string += 'Description:'
    return prompt_string


def format_description(description):
    """
    Breaks descriptions into sentences and the creates format with first paragraph,
    body (bullet points array) and last paragraph
    """
    sentences = list(map(str.strip, description.split('.')[:-1]))
    sentences = [f'{sentence}.' for sentence in sentences]
    formatted_description = {
        'first_paragraph': sentences[0],
        'body': sentences[1:-1],
        'last_paragraph': sentences[-1]
    }
    return formatted_description
