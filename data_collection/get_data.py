from pymongo import MongoClient
import json
import os
import logging
import requests
import time

# Configure logging
logging.basicConfig(
    filename='logs.txt',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

MONGO_URI = "mongodb://localhost:27017/"
REMAINING_JSON = os.path.join(os.getcwd(), 'remaining.json')
INPUT_JSON = os.path.join(os.getcwd(), 'response.json')
TIME_BETWEEN = 5  # seconds


client = MongoClient(MONGO_URI)
db = client.bachelor

def fetch_package_details(repo_name, package_name):
    url = f'https://artifacthub.io/api/v1/packages/helm/{repo_name}/{package_name}'
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def fetch_security_report(package_id, version):
    url = f'https://artifacthub.io/api/v1/packages/{package_id}/{version}/security-report'
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def setup_db():
    """Initializes the MongoDB database and cleans collections"""

    if "packages" not in db.list_collection_names():
        db.create_collection("packages")
        print("Database 'bachelor' and collection 'packages' ensured.")
    else:
        print("Database 'bachelor' already exists with 'packages'.")

    if "reports" not in db.list_collection_names():
        db.create_collection("reports")
        print("Database 'bachelor' and collection 'reports' ensured.")
    else:
        print("Database 'bachelor' already exists with 'reports'.")

    # Remove all documents from all collections in the 'bachelor' database
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        collection = db[collection_name]
        delete_result = collection.delete_many({})
        print(f"Removed {delete_result.deleted_count} documents from collection '{collection_name}'.")

def _sanitize_keys(obj):
    """Recursively sanitizes dictionary keys by replacing dots with __dot__."""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_key = k.replace('.', '__dot__')
            new_obj[new_key] = _sanitize_keys(v)
        return new_obj
    elif isinstance(obj, list):
        return [_sanitize_keys(item) for item in obj]
    else:
        return obj

def save_json(data, collection_name, identifier):
    """Saves the given data to the specified collection in MongoDB."""
    try:
        collection = db[collection_name]
        sanitized_data = _sanitize_keys(data) # Sanitize keys before insertion
        insert_result = collection.insert_one(sanitized_data)
        logging.info(f"Successfully saved data for {identifier} to collection {collection_name} with id {insert_result.inserted_id}")
    except Exception as e:
        logging.error(f"Failed to save data for {identifier} to collection {collection_name}: {e}")


def main():
    package_counter = 0
    report_counter = 0

    setup_db()

    # Load index data
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        charts = json.load(f)

    print(f"Loaded {len(charts)} charts from {INPUT_JSON}")

    remaining = []
    for index, chart in enumerate(charts, start=1):
        if index % 100 == 0:
            logging.info(f"Processed {index} charts so far.")
        logging.info(f"Processing chart: {chart}")

        name = chart.get('name')
        version = chart.get('version')
        repo = chart.get('repository', {}).get('name')
        identifier = f"{repo}/{name}@{version}"

        try:
            # Fetch details
            details = fetch_package_details(repo, name)
            save_json(details, "packages", identifier)
            logging.info(f"Successfully downloaded details for {identifier}")
            package_counter += 1

            # Fetch security report
            pkg_id = details.get('package_id')
            report = fetch_security_report(pkg_id, version)
            save_json(report, "reports", identifier)
            logging.info(f"Successfully downloaded security report for {identifier}")
            report_counter += 1

            # Success: do not re-add to remaining
        except requests.HTTPError as he:
            logging.error(f"%s - HTTP error: %s", identifier, he)
            remaining.append(chart)
        except Exception as e:
            logging.error(f"%s - Unexpected error: %s", identifier, e)
            remaining.append(chart)

        time.sleep(TIME_BETWEEN)
    # Rewrite YAML with remaining charts
    with open(REMAINING_JSON, 'w', encoding='utf-8') as f:
        json.dump(remaining, f, indent=2)

    logging.info(f"Total packages processed: {package_counter}")
    logging.info(f"Total reports processed: {report_counter}")
    logging.info(f"Remaining packages: {len(remaining)}")

if __name__ == '__main__':
    main()