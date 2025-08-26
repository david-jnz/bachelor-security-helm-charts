import json
import subprocess
from pymongo import MongoClient
import os
import logging

logging.basicConfig(
    filename='config_scan_logs.txt',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

INPUT_JSON = os.path.join(os.getcwd(), 'response.json')
client = MongoClient("mongodb://localhost:27017/")
db = client.bachelor
if "packages" not in db.list_collection_names():
        db.create_collection("configscan")



def scan_chart(chart_name, chart_version, repo_url, repo_name):
    #add repo
    try:
        subprocess.run(f"helm repo add {repo_name} {repo_url}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Hinzufügen des Repositories: {e}")
        return
    
    #pull chart
    try:
        subprocess.run(f"helm pull {repo_name}/{chart_name} --version {chart_version} --untar", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Herunterladen des Helm Charts {chart_name}: {e}")
        return
    
    #lint chart 
    try: 
        result = subprocess.run(f"kube-linter lint {chart_name}/ --format json", shell=True, capture_output=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        result = e
    
    #parse output
    try:
        linter_output = json.loads(result.stdout)
        if "Checks" in linter_output:
            linter_output.pop("Checks")
    except json.JSONDecodeError as e:
        logging.error(f"Fehler beim Parsen der Linter-Ausgabe für {chart_name}: {e}")
        return
    
    #save to mongodb
    collection = db["configscan"]
    chart_data = {
        "name": chart_name,
        "version": chart_version,
        "repository": repo_name,
        "linter_output": linter_output
    }
    try:
        collection.insert_one(chart_data)
        logging.info(f"Erfolgreich: Scan für {chart_name} ({chart_version}) wurde in der Datenbank gespeichert.")
    except Exception as e:
        logging.error(f"Fehler beim Speichern des Scans für {chart_name} in der Datenbank: {e}")
        return
    
    #remove dir
    try:
        subprocess.run(f"rm -rf {chart_name}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Entfernen des Verzeichnisses für {chart_name}: {e}")
        return

def main():
    #clear mongodb collection
    db["configscan"].delete_many({})
    logging.info("Starte den Scan von Helm Charts...")

    #load data from json file
    try:
        with open(INPUT_JSON, "r") as f:
            helm_charts = json.load(f)
    except FileNotFoundError:
        logging.error("Fehler: response.json nicht gefunden.")
        return
    except json.JSONDecodeError:
        logging.error("Fehler: response.json ist kein gültiges JSON.")
        return
    
    for chart in helm_charts:
        chart_name = chart.get("name")
        chart_version = chart.get("version")
        repository = chart.get("repository", {})
        repo_url = repository.get("url")
        repo_name = repository.get("name")

        scan_chart(chart_name, chart_version, repo_url, repo_name)
    logging.info("Alle Helm Charts wurden erfolgreich gescannt und in der Datenbank gespeichert.")


if __name__ == "__main__":
    main()