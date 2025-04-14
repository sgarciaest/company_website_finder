from flask import Flask, request, jsonify
from standardize_functions import normalize_company_name
from domain_functions import get_main_page, check_domain_for_company, bing_search
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "Use the /find_website endpoint. Example: /find_website?company=Apple Inc."

@app.route('/find_website', methods=['GET'])
def find_website():
    try:
        name = request.args.get('company', "PayPal Europe S.a.r.l. et C")


        if not name:
            return jsonify({"error": "Missing required query parameter: 'company'"}), 400

        standardized_name = normalize_company_name(name)

        urls = bing_search(f"{name} website")

        preferred_tld = [".com", ".org", ".net", ".edu", ".gov"]
        preferred_domain = None

        valid_domains = list(set([
            get_main_page(url)
            for url in urls
            if check_domain_for_company(standardized_name, url)
        ]))

        if not valid_domains:
            return jsonify({
                'company': name,
                'standardized_name': standardized_name,
                'status': 'no_matches',
                'website(s)': []
            })

        elif len(valid_domains) == 1:
            return jsonify({
                'company': name,
                'standardized_name': standardized_name,
                'status': 'valid_domain',
                'website(s)': [valid_domains[0]]
            })

        else:
            # Multiple domains found
            unique_valid_domains = list(set(valid_domains))

            for domain in unique_valid_domains:
                if any(tld in domain for tld in preferred_tld):
                    preferred_domain = domain
                    break

            if preferred_domain:
                unique_valid_domains.remove(preferred_domain)
                ordered_domains = [preferred_domain] + unique_valid_domains
            else:
                ordered_domains = unique_valid_domains

            return jsonify({
                'company': name,
                'standardized_name': standardized_name,
                'status': 'multiple_matches',
                'website(s)': ordered_domains
            })

    except Exception as e:
        app.logger.exception("Unhandled error in /find_website")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
