from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(filename='analysis_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = MongoClient("mongodb://localhost:27017/")
db = client.bachelor
collection_packages = db.packages
collection_reports = db.reports

all_packages = []
all_reports = []
sec_counter = 0

for doc in collection_packages.find():
    all_packages.append(doc)
    if 'security_report_summary' in doc:
        sec_counter += 1
    
logging.info(f"Total packages in db: {len(all_packages)}")
logging.info(f"Total packages with security reports: {sec_counter}")

try: 
    for doc in collection_reports.find():
        all_reports.append(doc)
except Exception as e:
    logging.error(f"Error while fetching reports: {e}")

logging.info(f"While there are {sec_counter} reports available, only {len(all_reports)} reports were saved in the db.")