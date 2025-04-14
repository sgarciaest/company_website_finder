import re
import json
import pycountry
import hashlib
import string
import csv

# Normalizes a string by replacing accented characters, converting to lowercase, removing special characters, and ensuring consistent whitespace.
def lower_and_manage_special(name):
    # Replace accented characters by the normal character
    replacements = {
        'á': 'a',
        'é': 'e',
        'í': 'i',
        'ó': 'o',
        'ú': 'u',
        'Á': 'a',
        'É': 'e',
        'Í': 'i',
        'Ó': 'o',
        'Ú': 'u',
        'ñ': 'n',
        'Ñ': 'n'
    }
    for accented_char, replacement in replacements.items():
        name = name.replace(accented_char, replacement)

    # Replace separation symbols by whitespace
    name = re.sub(r'[&\'\+\-,\.]', " ", name)

    # Convert to lowercase
    name = name.lower()

    # Remove any other special characters not removed yet
    name = re.sub(r'[^a-z0-9 ]', '', name)

    # Ensure there are no additional whitespaces (e.g. two whitespaces between two words instead of one)
    name = " ".join(name.split())

    return name

def load_legal_designations():
    # Load the JSON file for legal designations for companies
    with open('./data/raw/company_legal_designations.json', 'r') as file:
        legal_designations_data = json.load(file)
    return legal_designations_data

def load_country_names():
    # Load the JSON file for country names (names both in english and local language of the company) 
    with open('./data/raw/country_names.json', 'r') as file:
        country_names_data = json.load(file)
    return country_names_data

def define_suffixes_re_pattern():
    # Get all unique legal designations and add to a set
    all_suffixes = set()
    legal_designations_data = load_legal_designations()
    country_names_data = load_country_names()
    for key, designations in legal_designations_data.items():
        for designation in designations:
            designation = lower_and_manage_special(designation)
            all_suffixes.add(designation)

    # Get all unique country names and add to set with the legal designations
    for country in country_names_data["countries"]:
        for country_name in country.values():
            country_name = lower_and_manage_special(country_name)
            all_suffixes.add(country_name)

    # Convert the designations into a regex pattern (case insensitive)
    pattern = r'\b(' + '|'.join(re.escape(term) for term in all_suffixes) + r')\b'

    return pattern


# Function to normalize company names
def normalize_company_name(name):
    # Convert to lowercase and remove special characters using function created above
    name = lower_and_manage_special(name)
    # Replace "&"" with "and"
    name = re.sub(r'[&]', 'and', name)
    #Load the regex pattern
    pattern = define_suffixes_re_pattern()
    # Remove legal designations and other suffixes using the pattern created
    # Any text after a possible legal designation or suffix is also descarted
    split_name = re.split(pattern, name, flags=re.IGNORECASE)
    name = split_name[0].strip()
    # Remove whitespaces
    # name = name.replace(" ", "")
    # Eliminar palabras de una sola letra (!?)
    name = ' '.join([word for word in name.split() if len(word) > 1])
    # Return the cleaned name
    return name
