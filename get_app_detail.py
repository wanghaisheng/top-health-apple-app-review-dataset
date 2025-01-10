import requests
import os
import hashlib
import concurrent.futures
from DataRecorder import Recorder
from getbrowser import setup_chrome
from dotenv import load_dotenv
from  save_app_profile import *
from datetime import datetime
import json
load_dotenv()

# Constants for D1 Database
D1_DATABASE_ID = os.getenv('CLOUDFLARE_D1_DATABASE_ID')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')

CLOUDFLARE_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}"

# Initialize Browser
browser = setup_chrome()

def getinfo(url):
    """
    Scrape app information from the provided URL.
    """
    if url:
        try:
            tab = browser.new_tab()
            tab.get(url)
            print(f'get info for {url}')
            # Extract app details
            appid = url.split('/')[-1]
            appname = url.split('/')[-2]
            country = url.split('/')[-4]
            current_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            
            updated_at = current_time
            
            # Extract version information
            tab.ele('.version-history').click()
            version = tab.ele('.we-modal__content__wrapper').texts()[-1]
            version_list=version.split('\n')
            version_objects = [
        {"version": version_list[i], "date": version_list[i+1], "notes": version_list[i+2]}
        for i in range(0, len(version_list), 3)
        if i + 2 < len(version_list)  # Ensure there are at least three elements
    ]

            version_json = json.dumps(version_objects)  # Convert to JSON string
            print('find version',version_json)

            # version=version.replace('\n','--')
            tab.ele('.we-modal__close').click()
            # Extract additional information
            e = tab.ele('.information-list__item l-column small-12 medium-6 large-4 small-valign-top information-list__item--seller')
            print('find detail',e.texts())
            seller = e.text
            size = e.next().text
            print('find size',e.next().text)
            
            category = e.next(2).text
            lang = e.next(4).text
            age = e.next(5).text
            copyright = e.next(6).text
            pricetype = e.next(7).text
            priceplan=''
            if e.next(8):
                if e.next(8).ele('.we-truncate__button we-truncate__button--top-offset link'):
                    e.next(8).ele('.we-truncate__button we-truncate__button--top-offset link').click()
                priceplan = e.next(8).texts()[-1]
                if '\n' in priceplan:
                    priceplan=priceplan.split('\n')
                    priceplan_objects = [

                    {"item": priceplan[i], "price": priceplan[i+1]}
                            for i in range(0, len(priceplan), 2)
                    if i + 1 < len(priceplan)  # Ensure there are at least three elements
                        ]
                    priceplan = json.dumps(priceplan_objects)  # Convert to JSON string


            website=tab.ele('.link icon icon-after icon-external').link
            # version_json=''
            # priceplan=''
            # Return app information as a dictionary
            return {
                "url": url,
                "appid": appid,
                "appname": appname,
                "country": country,
                "updated_at": updated_at,
                "releasedate": '',  # Assuming the last version is the latest
                "version": version_json,
                "seller": seller.split('\n')[-1] if '\n' in seller else seller,
                "size": size.split('\n')[-1] if '\n' in size else size,
                "category": category.split('\n')[-1] if '\n' in category else category,
                "lang": lang.split('\n')[-1] if '\n' in lang else lang,
                "age": age.split('\n')[-1] if '\n' in age else age,
                "copyright": copyright.split('\n')[-1] if '\n' in copyright else copyright,
                "pricetype": pricetype.split('\n')[-1] if '\n' in pricetype else pricetype,                
                "priceplan": priceplan,
                "lastmodify":current_time,
                'website':website
            }
        except Exception as e:
            print(f"Error fetching info for {url}: {e}")
            return None

def bulk_scrape_and_save_app_urls(urls):
    """
    Scrape app information for multiple URLs concurrently and save to D1 database.
    """
    create_app_profiles_table()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(getinfo, urls))
    
    batch_process_in_chunks(results, process_function=batch_process_initial_app_profiles)
if __name__ == "__main__":
    # Create the table before scraping
    create_app_profiles_table()

    # List of URLs to scrape
    urls = [
        "https://apps.apple.com/us/app/captiono-ai-subtitles/id6538722927",
        "https://apps.apple.com/us/app/example-app/id1234567890"
    ]

    # Perform scraping and save to D1
    bulk_scrape_and_save_app_urls(urls)
