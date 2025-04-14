from domain_functions import get_main_page, remove_separation_symbols, check_domain_for_company, bing_search
import json
from pymongo import MongoClient


# Load the preprocessed suppliers file as json.
with open("../data/processed/preprocessed_data.json", "r", encoding="utf-8") as file:
    preprocessed_data = json.load(file)

# MongoDB Connection
password = "IxQm3BVUYcCjpegr"
connection_string = f"mongodb+srv://valumiaesade-admin:{password}@valumiaesade-cluster.avqms.mongodb.net/"
client = MongoClient(connection_string)
db = client["valumia"]
collection = db["suppliers"]

for supplier in preprocessed_data:
    domain = supplier["data"]["domain"]
    print(domain)
    print(type(domain))
    name = supplier["data"]["name"]
    standardized_name = supplier["data"]["standardized_name"]
    supplier_id = supplier["id"]
    
    if domain != None:
        print("domain given by user")
        continue

    existing_record = collection.find_one({"id": supplier_id})

    if existing_record:
        print("supplier domain found on mongodb")
        supplier["data"]["domain"] = existing_record["data"]["domain"]
        supplier["data"]["domain_status"] = "valid_domain"
        continue

    if not domain or domain == "" or domain.lower() in ["nan", "unknown", "none"]:
        
        # Create empty list to store the urls gathered from binga
        urls = []

        print(f"Recipient of the payment: {name}")

        # Print the URL results from the bing search query
        print(f"Searching for potential domains for '{name}' using Bing ...")
        for url in bing_search(f"{name} website"):
        # for url in search(f"{name} website", num_results=3):
            urls.append(url)
        print(f"First URLs found on Bing when searching for '{standardized_name} website':")
        for i, url in enumerate(urls, 1):
            print(f"{i}: {url}")

        preferred_tld = [".com", ".org", ".net", ".edu", ".gov"]
        preferred_domain = 0

        # Evaluate URLs with check_domain_for_company and store the valid domains in a list
        valid_domains = list(set([get_main_page(url) for url in urls if check_domain_for_company(standardized_name, url)]))

        # For each possible case with valid domains(no valid domains found, one valid domain found and multiple valid domains found), print a message and save the valid domains and state to the output df
        if len(valid_domains) == 0:
            # No valid domain found
            print(f"No exact matches for valid domains were found for '{name}'. The user will be asked for manual input later.")
            supplier["data"]["domain"] = []
            supplier["data"]["domain_status"] = "no_matches"
            
        elif len(valid_domains) == 1:
            # Only one valid domain found
            print(f"A valid domain was found for '{name}': {valid_domains[0]}")
            supplier["data"]["domain"] = [valid_domains[0]]
            supplier["data"]["domain_status"] = "valid_domain"

        else:
            # Multiple valid domains found
            unique_valid_domains = list(set(valid_domains))  # Remove duplicates, keeping only unique values
            print(f"Multiple valid domains were found for '{name}':")
            for i, domain in enumerate(unique_valid_domains, 1):  # Enumerate unique domains
                print(f"{i}: {domain}")

                if any(tld in domain for tld in preferred_tld):
                    preferred_domain = domain
            
            # If a preferred domain TLD is found, it is saved in the Domain column and the rest in the Alternate Domains column. Still, a manual check by the user would be needed.
            if preferred_domain == 0:
                supplier["data"]["domain"] = unique_valid_domains
                supplier["data"]["domain_status"] = "multiple_matches"

            else:
                index_preferred_domain = unique_valid_domains.index(preferred_domain)
                unique_valid_domains = [preferred_domain] + unique_valid_domains[:index_preferred_domain] + unique_valid_domains[index_preferred_domain + 1:]
                supplier["data"]["domain"] = unique_valid_domains
                supplier["data"]["domain_status"] = "multiple_matches"

        # Save the output dataframe in a csv file in each iteration (everytime a new standardized_name is added) 
        # Save to file
        output_path = "../data/processed/validation_view_output.json"
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(preprocessed_data, output_file, indent=4, ensure_ascii=False)
        print("-------------------------------")


# Save to file
output_path = "../data/processed/validation_view_output.json"

with open(output_path, "w", encoding="utf-8") as output_file:
    json.dump(preprocessed_data, output_file, indent=4, ensure_ascii=False)

print(f"List of suppliers processed with domains and saved to {output_path}")