# bachelor-security-helm-charts
This repository contains the code for bachelor thesis "Security in Helm Charts: Vulnerabilities and misconfigurations"

## Overview

This project explores security in public Helm Charts. The repository includes source code, documentation, and examples.

## Getting Started

Start the docker mongo container:

```bash
docker run --name bachelor-mongodb -p 27017:27017 -v mongo-data:/data/db -d mongo:latest
```

Starting the python script in background:
```bash
nohup python3 get_data.py > output.log 2>&1 &
```

## Saving mongodb dump from server to local db-container

```bash
ssh -i "C:\Users\David\OneDrive\Projekte\Webdesign\Webseiten\Hosting\ssh-key-2025-02-12.key" ubuntu@158.180.32.121 "docker exec bachelor-mongodb mongodump --db=bachelor --archive --gzip" | docker exec -i bachelor-mongodb mongorestore --archive --gzip --nsInclude='bachelor.*'
```