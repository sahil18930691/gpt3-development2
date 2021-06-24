#!usr/bin/python
import json

from babel.numbers import format_currency


def get_examples(property_type, listing_type=None):
    """
    Get all the examples from the JSON file for the specified
    property_type and listing_type
    """
    if listing_type is None:
        json_path = f'prompts/{property_type}.json'
    else:
        json_path = f'prompts/{property_type}_{listing_type}.json'
    with open(json_path, 'rb') as json_file:
        examples = json.loads(json_file.read())
    return examples


def format_listing_data(listing_data):
    """
    Formats the examples for usage in the prompt
    """
    prompt_string = ""
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

    if "bedrooms" in listing_data:
        prompt_string += f"Bedrooms: {listing_data['bedrooms']}\n"

    if "bathrooms" in listing_data:
        prompt_string += f"Bathrooms: {listing_data['bathrooms']}\n"

    if "parking" in listing_data:
        prompt_string += f"Parking: {listing_data['parking']}\n"
    
    if "price" in listing_data:
        formatted_price = format_currency(listing_data['price'], 'INR', locale='en_IN')[1:].split('.')[0]
        prompt_string += f"Price: {formatted_price}\n"
    
    if "area" in listing_data:
        prompt_string += f"Area: {listing_data['area']} {listing_data['area_unit']}\n"
    
    if "facing" in listing_data:
        prompt_string += f"Facing: {listing_data['facing']}\n"
    
    if "property_age" in listing_data:
        prompt_string += f"Property Age: {listing_data['property_age']}\n"
    
    if "floor_number" in listing_data:
        prompt_string += f"Floor number: {listing_data['floor_number']}\n"
    
    if "total_floor_count" in listing_data:
        prompt_string += f"Total Floor Count: {listing_data['total_floor_count']}\n"

    if "amenities" in listing_data:
        prompt_string += f"Amenities: {listing_data['amenities']}"

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
    prompt_string += 'Description: '
    return prompt_string
