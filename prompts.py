#!/usr/bin/python
import os
import re
import json

from fastapi import HTTPException
from babel.numbers import format_currency

from utils import logger, hit_gpt_api
from text_processing import get_tokens,\
                            get_scores,\
                            get_best_description,\
                            encode_description_to_preserve_some_tokens,\
                            remove_encodings,\
                            fix_description,\
                            fix_furnish


TOKEN_COVERAGE_THRESHOLD = 0.40
# After this many iterations. No fixing will be done.
# This is done to avoid infinite loops.
FIXING_ITERATIONS = 30
# Number of times the program is going to hit GPT-3 in case the 
# returned descriptions are not up to the mark.
API_HIT_ITERATIONS_THRESHOLD = 2
# Number of descriptions to be returned by GPT-3 in each request.
NUM_EXAMPLES = 2

# GPT-3 payload.
BASE_PAYLOAD = {
    "max_tokens": 300,
    "temperature": 0.5,
    "top_p": 0.8,
    "n": NUM_EXAMPLES,
    "stream": False,
    "logprobs": None,
    "stop": ["-----"]
}


async def generate_description(listing_data, format=False):
    """
    Generates a description for any type of BaseListingData.
    Steps:
        1. Hit the API
        2. Find best description from returned description using scoring.
        3. If description is acceptable then return it.
        4. If it is not acceptable. Repeat steps 1-3 certain number of times before giving up.
    """

    listing_data_dict = dict(listing_data)
    keywords = []
    for key, vals in listing_data_dict.items():
        token_list = get_tokens(vals)
        keywords.extend(token_list)

    payload = dict(BASE_PAYLOAD)
    payload['prompt'] = create_prompt(listing_data)
    
    data = await hit_gpt_api(payload)
    description_scores, data = get_scores(data, set(keywords))
    # for i in range(len(description_scores)):
    #     print(data["choices"][description_scores[i][2]]["text"])
    #     print(description_scores[i][0], description_scores[i][1])
    #     print("--xx--")
    description = None

    description, correct_description_found, unique_token_score, token_coverage_score = get_best_description(data, description_scores)

    # Again hit the GPT-3 API in case we don't get a satisfactory description.
    hit_iterations = 1
    while hit_iterations < API_HIT_ITERATIONS_THRESHOLD and correct_description_found == False:
        new_data = await hit_gpt_api(payload)

        for new_description in new_data['choices']:
            data['choices'].append(new_description)
        description_scores, data = get_scores(data, set(keywords))

        description, correct_description_found, unique_token_score, token_coverage_score = get_best_description(data, description_scores)
        hit_iterations += 1

    # Return error if we API is unable to find description.
    if correct_description_found == False and token_coverage_score < TOKEN_COVERAGE_THRESHOLD:
        logger.info("-------->>  Failed for prompt: \n"+str(payload['prompt']))
        logger.info("========>> Best description for failed prompt: \n"+str(description))
        raise HTTPException(status_code=500, detail="Could not generate the description for the given input.")

    # if format:
    #     description = format_description(description)

    description_copy = description
    try:
        cnt = 0
        modified = True
        while modified and cnt < FIXING_ITERATIONS:
            cnt += 1
            description_copy = re.sub(" +", " ", description_copy)
            description_copy, modified = encode_description_to_preserve_some_tokens(description_copy)
        
        description_copy = description_copy.replace("-", " ")
        description_copy = remove_encodings(description_copy)
        description_copy = description_copy.replace("bhk", " bhk")\
                                            .replace(" rs.", " rs ")
    except:
        pass

    try:
        description_copy = re.sub(" +", " ", description_copy)
        modified = True
        cnt = 0
        print(description_copy)
        while modified and cnt < FIXING_ITERATIONS:
            cnt += 1
            description_copy, modified = fix_description(description_copy, listing_data)
    except:
        pass

    # Fixing for furnish
    try:
        description_copy = fix_furnish(description_copy, listing_data.furnishing.replace("-", " "))
    except:
        pass
    description_copy = re.sub(" +", " ", description_copy).strip()
    description_copy = description_copy.replace(" rs ", " Rs ")

    if format:
        description_copy = format_description(description_copy)
        
    return description_copy


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
        if listing_data["bathrooms"] != 0:
            prompt_string += f"Bathrooms: {listing_data['bathrooms']}\n"
    
    if "pantry" in listing_data:
        prompt_string += f"Pantry: {listing_data['pantry']}\n"
    
    if "washroom_present" in listing_data:
        prompt_string += f"Washroom Present: {listing_data['washroom_present']}\n"

    if "parking" in listing_data:
        if listing_data["parking"] != 0:
            prompt_string += f"Parking: {listing_data['parking']}\n"
    
    if "price" in listing_data:
        formatted_price = format_currency(listing_data['price'], 'INR', locale='en_IN')[1:].split('.')[0]
        prompt_string += f"Price: {formatted_price}\n"
    
    # Concatenate area and area_unit and remove full stops, if any
    if "area" in listing_data and "area_unit" in listing_data:
        prompt_string += f"Area: {listing_data['area']} {listing_data['area_unit'].replace('.', '')}\n"
    
    if "facing" in listing_data:
        prompt_string += f"Facing: {listing_data['facing']}\n"
    
    if "property_age" in listing_data:
        prompt_string += f"Property Age: {listing_data['property_age']}\n"
    
    if "plot_number" in listing_data:
        prompt_string += f"Plot Number: {listing_data['plot_number']}\n"
    
    if "floor_number" in listing_data:
        if listing_data["floor_number"] != 0:
            prompt_string += f"Floor number: {listing_data['floor_number']}\n"
        
    if "total_floor_count" in listing_data:
        if listing_data["total_floor_count"] != 0:
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
    sentences = list(map(str.strip, description.split('. ')[:-1]))
    sentences = [f'{sentence}.' for sentence in sentences]
    formatted_description = {
        'first_paragraph': sentences[0],
        'body': sentences[1:-1],
        'last_paragraph': sentences[-1]
    }
    return formatted_description

