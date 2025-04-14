from flask import Flask, request, jsonify
from standardize_functions import normalize_company_name
from domain_functions import get_main_page, check_domain_for_company, bing_search


app = Flask(__name__)

@app.route('/')
def home():
    return "Use /find_website endpoint"

@app.route('/find_website', methods=['GET'])
def find_website():
    name = request.args.get('company', "PayPal Europe S.a.r.l. et C")
    print(name)
    print(type(name))
    standardized_name = normalize_company_name(name)

    # Create empty list to store the urls gathered from binga
    urls = []

    for url in bing_search(f"{name} website"):
    # for url in search(f"{name} website", num_results=3):
        urls.append(url)

    preferred_tld = [".com", ".org", ".net", ".edu", ".gov"]
    preferred_domain = 0

    valid_domains = list(set([get_main_page(url) for url in urls if check_domain_for_company(standardized_name, url)]))

    # For each possible case with valid domains(no valid domains found, one valid domain found and multiple valid domains found), print a message and save the valid domains and state to the output df
    if len(valid_domains) == 0:
        # No valid domain found
        return jsonify({'company': name, 'standardized_name': standardized_name, "website(s)": "No website found"})
        
    elif len(valid_domains) == 1:
        # Only one valid domain found
        return jsonify({'company': name, 'standardized_name': standardized_name, "website(s)": [valid_domains[0]]})

    else:
        # Multiple valid domains found
        unique_valid_domains = list(set(valid_domains))  # Remove duplicates, keeping only unique values
        for i, domain in enumerate(unique_valid_domains, 1):  # Enumerate unique domains
            if any(tld in domain for tld in preferred_tld):
                preferred_domain = domain
        
        # If a preferred domain TLD is found, it is put first
        if preferred_domain == 0:
            supplier["data"]["domain"] = unique_valid_domains
            supplier["data"]["domain_status"] = "multiple_matches"
            return jsonify({'company': name, 'standardized_name': standardized_name, "website(s)": unique_valid_domains})

        else:
            index_preferred_domain = unique_valid_domains.index(preferred_domain)
            unique_valid_domains = [preferred_domain] + unique_valid_domains[:index_preferred_domain] + unique_valid_domains[index_preferred_domain + 1:]
            return jsonify({'company': name, 'standardized_name': standardized_name, "website(s)": unique_valid_domains})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
