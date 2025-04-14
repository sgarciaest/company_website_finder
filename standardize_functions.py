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

def load_suffixes():
    with open('./data/updated_valumia.countries.extra.ld.json', 'r') as file:
        countries_db = json.load(file)
    with open('./data/other_suffixes.json', 'r') as file:
        other_suffixes = json.load(file)
    all_sufixes = set()

    for country in countries_db:
        for ld in country["legal_designations"]:
            abbreviations = ld["abbreviation"]
            for abbreviation in abbreviations:
                abbreviation = lower_and_manage_special(abbreviation)
                all_sufixes.add(abbreviation)
    for lang_data in country["native_names"].values():
        native_name_official = lang_data["official"]
        native_name_official = lower_and_manage_special(native_name_official)
        all_sufixes.add(native_name_official)
        native_name_common = lang_data["common"]
        native_name_common = lower_and_manage_special(native_name_common)
        all_sufixes.add(native_name_common)
    
    for g in other_suffixes.values():
        for suffix in g:
            suffix = lower_and_manage_special(suffix)
            all_sufixes.add(suffix)
    
    return all_sufixes


# Function to normalize company names
def normalize_company_name(name):
    all_suffixes = load_suffixes()

    # Convert to lowercase and remove special characters using function created above
    name = lower_and_manage_special(name)
    
    # Replace "&"" with "and"
    name = name.replace("&", "and")

    # Tokenizar el nombre en palabras
    palabras = name.split()

    # Eliminar palabras que sean sufijos legales
    palabras_filtradas = [word for word in palabras if word not in all_suffixes]

    # Reconstruir el nombre limpio
    name = " ".join(palabras_filtradas)
    
    # Eliminar palabras de una sola letra (!?)
    name = ' '.join([word for word in name.split() if len(word) > 1])
    
    # Return the cleaned name
    return name
