import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


D1_DATABASE_ID = os.getenv('CLOUDFLARE_D1_DATABASE_ID')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}"
url = f"{CLOUDFLARE_BASE_URL}/query"
print('=======',url,CLOUDFLARE_ACCOUNT_ID,D1_DATABASE_ID,CLOUDFLARE_API_TOKEN)
def create_category_urls_table():
    """
    Create the ios_top100_category_urls table if it does not exist in the D1 database.
    """
    url = f"{CLOUDFLARE_BASE_URL}/query"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # SQL query to create the table if it doesn't exist
    sql_query = """
    CREATE TABLE IF NOT EXISTS ios_top100_category_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        country TEXT NOT NULL,
        cid TEXT NOT NULL,
        cname TEXT NOT NULL,
        url TEXT NOT NULL
    );
    """

    payload = {"sql": sql_query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Table 'ios_top100_category_urls' created successfully (if it didn't exist).")
    except requests.RequestException as e:
        print(f"Failed to create table ios_top100_category_urls: {e}")

def save_category_urls_to_d1(category_urls):
    """
    Save category URLs to the D1 database.
    """
    url = f"{CLOUDFLARE_BASE_URL}/query"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    create_category_urls_table()


    values = []
    for category_url in category_urls:
        parsed_url = urlparse(category_url)
        path_parts = parsed_url.path.split('/')
        platform = path_parts[-3]
        country = path_parts[-5]
        cid = path_parts[-1]
        cname = path_parts[-2]

        values.append(f"('{platform}', '{country}', '{cid}', '{cname}', '{category_url}')")

    sql_query = "INSERT INTO ios_top100_category_urls (platform, country, cid, cname, url) VALUES "
    sql_query += ", ".join(values) + ";"

    payload = {"sql": sql_query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Category URLs inserted successfully.")
    except requests.RequestException as e:
        print(f"Failed to insert category URLs: {e}")

# Example usage
# create_category_urls_table()

category_urls = [
    "https://www.example.com/us/ios/appstore/category/123/Adventure",
    "https://www.example.com/uk/ios/appstore/category/456/Action",
    "https://www.example.com/us/ios/appstore/category/789/Puzzle"
]
# save_category_urls_to_d1(category_urls)
