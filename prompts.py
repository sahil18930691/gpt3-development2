#!/usr/bin/python
import os
import re
import json
import requests

from dotenv import load_dotenv
from fastapi import HTTPException
from nltk.stem import PorterStemmer
from babel.numbers import format_currency

from matchers import nlp

# loading environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT')
TOKEN_COVERAGE_THRESHOLD = 0.35
UNIQUE_TOKEN_THRESHOLD = 0.43
TOKEN_THRESHOLD = 15
API_HIT_ITERATIONS_THRESHOLD = 2
NUM_EXAMPLES = 2

BASE_PAYLOAD = {
    "max_tokens": 300,
    "temperature": 0.5,
    "top_p": 0.8,
    "n": NUM_EXAMPLES,
    "stream": False,
    "logprobs": None,
    "stop": ["-----"]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

ps = PorterStemmer()


def get_tokens(sentence_):
    """
    Function to tokenize the input sentence.
    """
    sentence_ = f"{sentence_}".lower().strip()
    sentence_ = sentence_.replace("-", " ")
    sentence_ = re.sub(" +", " ", sentence_)
    doc = nlp(sentence_)
    tokens = []
    for token in doc:
        cur = token.lemma_
        try:
            cur = str(int(replace_nth(cur)))
        except:
            pass
        cur = re.sub(r"[()\"/;:<>{}`+=~|!?']", "", cur)
        cur = re.sub(r"[.,']", " ", cur)
        cur = re.sub(" +", " ", cur)
        digit_to_eng = cur.replace("1", "one")\
                            .replace("2", "two")\
                            .replace("3", "three")\
                            .replace("4", "four")\
                            .replace("5", "five")\
                            .replace("6", "six")\
                            .replace("7", "seven")\
                            .replace("8", "eight")\
                            .replace("9", "nine")\
                            .replace("0", "zero")

        if len(digit_to_eng) == len(cur) and len(cur.strip()) >=2:
            tokens.append(ps.stem(cur))
        else:
            tokens.append(digit_to_eng)

    return tokens


def get_description_scores(data, keywords):
    """
    Calculates the scores for a list of descriptions.
    """
    scores = []
    for idx in range(len(data['choices'])):
        description = data['choices'][idx]['text'].strip()
        description_keywords_list = get_tokens(description)
        description_keywords_set = set(description_keywords_list)
        common_keywords_set = keywords.intersection(description_keywords_set)
        s1 = 0
        s2 = 0
        if len(keywords) > 0:
            s1 = len(common_keywords_set) / len(keywords)
        if len(description_keywords_list) > 0:
            s2 = len(description_keywords_set) / len(description_keywords_list)
        score_ =  s1 + s2

        scores.append(score_)

    return scores


def remove_duplicate_sentences(description):
    try:
        sents = description.split(".")

        sent_dict = {}
        for sent in sents:
            sent_dict[sent] = "."

        new_sents = []
        for k, _ in sent_dict.items():
            new_sents.append(k)

        return_val = ".".join(new_sents)
        return return_val, return_val
    except Exception as e:
        print(e)
        print(description)
        
    return description, description


def get_scores(data, keywords):
    scores_token_coverage = []
    scores_unique_tokens = []
    for idx in range(len(data['choices'])):
        description = data['choices'][idx]['text'].strip()
        if description.count(":") >= 3 and (("description:" in description.lower()) or ("description :" in description.lower())):
            try:
                description = description[description.lower().rindex("description")+len("description"):]
                if ":" in description:
                    try:
                        idx_ = description.lower().find(":")
                        if idx_ != -1:
                            description = description[:idx_]
                            try:
                                description = description[:description.lower().rindex(" ")]
                            except:
                                pass
                    except:
                        pass
                description = description.replace(":", "").strip()
            except:
                pass
            data['choices'][idx]['text'] = description

        description, data['choices'][idx]['text'] = remove_duplicate_sentences(description)

        description_keywords_list = get_tokens(description)
        description_keywords_set = set(description_keywords_list)
        common_keywords_set = keywords.intersection(description_keywords_set)
        s1 = 0
        s2 = 0
        if len(keywords) > 0:
            s1 = len(common_keywords_set) / len(keywords)
        if len(description_keywords_list) > 0:
            s2 = len(description_keywords_set) / len(description_keywords_list)
        scores_token_coverage.append(s1)
        scores_unique_tokens.append(s2)

    scores = [(y, x, idx) for y, x, idx in sorted(zip(scores_token_coverage,\
                                                        scores_unique_tokens,\
                                                        list(range(len(scores_unique_tokens)))),\
                                                        key=lambda pair: pair[0])]

    return scores


def get_best_description(data, description_scores):
    correct_description_found = False
    description = None
    for i in range(len(description_scores)-1, -1, -1):
        cur_description = data['choices'][description_scores[i][2]]['text'].strip()
        if description_scores[i][1] >= UNIQUE_TOKEN_THRESHOLD and\
             len(get_tokens(cur_description)) >= TOKEN_THRESHOLD and\
             cur_description.count(":") <= 3:
            description = cur_description
            correct_description_found = True 
            return description, correct_description_found, description_scores[i][1], description_scores[i][0]

    max_coverage= max(description_scores, key=lambda x:x[1])
    description = data['choices'][max_coverage[2]]['text'].strip()
    return description, correct_description_found, max_coverage[1], max_coverage[0]


def hit_gpt_api(payload):
    """
    Function that sends a post request to GPT-3 API
    """
    try:
        response = requests.post(MODEL_ENDPOINT, headers=headers, data=json.dumps(payload))
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request to remote server failed: {str(e)}")

    return data


def generate_description(listing_data, format=False):
    """
    Generates a description for any type of BaseListingData
    """

    listing_data_dict = dict(listing_data)
    keywords = []
    for key, vals in listing_data_dict.items():
        token_list = get_tokens(vals)
        keywords.extend(token_list)

    payload = dict(BASE_PAYLOAD)
    payload['prompt'] = create_prompt(listing_data)
    
    data = hit_gpt_api(payload)
    description_scores = get_scores(data, set(keywords))
    # for i in range(len(description_scores)):
    #     print(data["choices"][description_scores[i][2]]["text"])
    #     print(description_scores[i][0], description_scores[i][1])
    #     print("--xx--")
    description = None
    description, correct_description_found, unique_token_score, token_coverage_score = get_best_description(data, description_scores)

    hit_iterations = 1
    while hit_iterations < API_HIT_ITERATIONS_THRESHOLD and correct_description_found == False:
        new_data = hit_gpt_api(payload)

        for new_description in new_data['choices']:
            data['choices'].append(new_description)
        description_scores = get_scores(data, set(keywords))

        # for i in range(len(description_scores)):
        #     print(data["choices"][description_scores[i][2]]["text"])
        #     print(description_scores[i][0], description_scores[i][1])
        #     print("--xx--")

        description, correct_description_found, unique_token_score, token_coverage_score = get_best_description(data, description_scores)
        hit_iterations += 1

    if correct_description_found == False and token_coverage_score < TOKEN_COVERAGE_THRESHOLD:
        print(description, correct_description_found, unique_token_score, token_coverage_score)
        raise HTTPException(status_code=500, detail="Could not generate the description for the given input.")

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
    if "area" in listing_data and "area_unit" in listing_data:
        prompt_string += f"Area: {listing_data['area']} {listing_data['area_unit'].replace('.', '')}\n"
    
    if "facing" in listing_data:
        prompt_string += f"Facing: {listing_data['facing']}\n"
    
    if "property_age" in listing_data:
        prompt_string += f"Property Age: {listing_data['property_age']}\n"
    
    if "plot_number" in listing_data:
        prompt_string += f"Plot Number: {listing_data['plot_number']}\n"
    
    if "floor_number" in listing_data:
        if listing_data["floor_number"] != 0
        prompt_string += f"Floor Number: {listing_data['floor_number']}\n"        
            
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
    print(prompt_string)
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

