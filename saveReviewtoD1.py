import hashlib
import requests
import os
from dotenv import load_dotenv

load_dotenv()

D1_DATABASE_ID = os.getenv('CLOUDFLARE_D1_DATABASE_ID')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')

CLOUDFLARE_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}"

def compute_hash(appid, username, date):
    """Compute a unique hash for each row."""
    hash_input = f"{appid}-{username}-{date}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


def create_table_if_not_exists():
    """Create the review table if it does not exist."""
    url = f"{CLOUDFLARE_BASE_URL}/query"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    create_query = """
        CREATE TABLE IF NOT EXISTS ios_review_data (
            id TEXT PRIMARY KEY,
            appid TEXT,
            appname TEXT,
            country TEXT,
            keyword TEXT,
            score REAL,
            userName TEXT,
            date TEXT,
            review TEXT
        );
    """
    try:
        response = requests.post(url, headers=headers, json={"sql": create_query})
        response.raise_for_status()
        print("Table created successfully.")
    except requests.RequestException as e:
        print(f"Failed to create table ios_review_data: {e}")

def insert_into_ios_review_data(data, batch_size=50):
    """Insert rows into the review table with hash checks and batch inserts."""
    url = f"{CLOUDFLARE_BASE_URL}/query"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    create_table_if_not_exists()
    
    if not data:
        print("No data to insert.")
        return

    for row in data:
            hash_id = compute_hash(row['appid'], row['userName'], row['date'])
            
            insert_query = (
                "INSERT OR IGNORE INTO ios_review_data (id, appid, appname, country, keyword, score, userName, date, review) "
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
            )
            
            values = (
                hash_id, row['appid'], row['appname'], row['country'], row['keyword'],
                 row['score'], row['userName'], row['date'], row['review']
            )
            try:
                response = requests.post(url, headers=headers, json={"sql": insert_query, "bindings": values})
                response.raise_for_status()
                print(f"Inserted row with id {hash_id} successfully.")
            except requests.RequestException as e:
                print(f"Failed to insert row with id {hash_id}: {e}\n{response.json()}")
