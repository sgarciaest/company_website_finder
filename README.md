# 🌐 Company Website Finder API

This lightweight Flask API helps you find the official website of a company based on its name. By leveraging Google search results and logic for domain evaluation, it intelligently identifies the most likely candidate domains.



Here’s the rewritten **Features** section, focused on clearly explaining the logic of the domain validation step-by-step. It avoids technical language, sticks to your tone, and highlights your design decisions so you can present it confidently on your GitHub profile:


## 🚀 Features

This API takes a company name and tries to find its possible official website by searching online and checking which domain is the most likely to belong to that company. Below are the key steps and ideas behind how it works:

### 1. Normalize the company name

The input company name is cleaned and simplified. This step is important because real company names often include legal suffixes or country-specific terms like:

- "Inc", "Ltd.", "S.A.", "GmbH", "LLC"
- "Group", "Solutions", "Partners"
- Country names or native official terms like "Republic of X"

To remove this extra information, the code:

- Converts all text to lowercase
- Replaces accented characters with simple letters (e.g. "é" → "e")
- Replaces symbols like commas, dots, ampersands with spaces
- Removes special characters
- Splits the name into words
- Removes short words (1 letter)
- Filters out suffixes found in two JSON files:
  - `updated_valumia.countries.extra.ld.json`: country legal suffixes and native names
  - `other_suffixes.json`: suffixes like "Solutions", "Technologies", "Capital", "Ventures", etc.

This leaves only the main keywords of the company name. For example:

```
Input: "Spotify AB"
→ Normalized: "spotify"

Input: "Global Holdings Group LLC"
→ Normalized: "global"
```

This logic is implemented in the `normalize_company_name()` function.


### 2. Search for candidate websites

The app sends a search query to Google like:

```
<company name> website
```

Then it collects a list of URLs from the top search results. The goal is to get real websites that are likely related to the company.



### 3. Extract and clean domains

Each search result URL is processed to extract the main domain (for example: `example.com`, `spotify.de`, `openai.org`). The function:

- Adds `https://` if it’s missing
- Uses the `tldextract` library to safely get the domain and TLD
- Falls back to regex if needed

This is done by the `get_main_page()` function.



### 4. Match normalized company name against domains

To check if a domain is likely related to the company, the API compares the normalized name with each domain.

For example, if the normalized name is `"airbnb"` and a domain is `"airbnb.com"`, then it's a match.

The check works by:
- Removing separation symbols from the domain (e.g. hyphens)
- Splitting the normalized name into words
- Checking if any word is contained in the cleaned domain

This is handled by the `check_domain_for_company()` function.



### 5. Return valid domains with ordering

All domains that pass the check are considered "valid". The API:

- Returns a single domain if only one is found
- Returns all if multiple are found
- Sorts them by TLD preference (`.com`, `.org`, `.net`, etc.)

Domains with preferred TLDs are listed first if found.



### 6. API Output

Example request:

```
GET /find_website?company=Spotify AB
```

Example response:

```json
{
  "company": "Spotify AB",
  "standardized_name": "spotify",
  "status": "valid_domain",
  "website(s)": ["spotify.com"]
}
```



Let me know if you'd like me to merge this into your full README or generate badges and metadata to complete the GitHub presentation.



## ⚠️ Legal & Ethical Considerations

This project currently relies on **unofficial scraping of Google Search** results using the `googlesearch-python` library and, optionally, **Bing search parsing via BeautifulSoup**.

> 🚨 Important Notes:
>
> - This method **violates the terms of service** of major search engines such as Google and Bing.
> - It is provided purely for **research, testing, and personal use**. The tool is **not intended for production deployment or high-frequency querying**.
> - Please do not use this system at scale or integrate into any application without understanding the legal and technical risks.


## 🛠️ Setup Instructions

You can replicate and run this locally by following these steps:

### 1. Clone the repository

```bash
git clone https://github.com/your-username/company-website-finder.git
cd company-website-finder
```

### 2. Build and run using Docker

```bash
docker build -t company-finder .
docker run -p 5000:5000 company-finder
```

### 3. Test the API

Visit:

```
http://localhost:5000/find_website?company=Spotify
```

You’ll receive a JSON response with one or more likely website matches.



## 📁 Project Structure

```
company_website_finder/
├── app/
│   ├── app.py                    # Flask API logic
│   ├── domain_functions.py       # Web search and domain extraction
│   ├── standardize_functions.py  # Company name normalization
│   └── data/
│       ├── other_suffixes.json
│       └── updated_valumia.countries.extra.ld.json
├── requirements.txt
├── Dockerfile
└── README.md
```



## ✅ Built With

- [Flask](https://flask.palletsprojects.com/)
- [tldextract](https://github.com/john-kurkowski/tldextract)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [googlesearch-python (unofficial)](https://github.com/Nv7-GitHub/googlesearch-python)
- Python 3.11+