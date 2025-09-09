# bachelor-security-helm-charts
This repository contains the code for bachelor thesis "Security in Helm Charts: Vulnerabilities and misconfigurations"

## Thesis & database dump
The thesis can be found [here](https://drive.google.com/file/d/1vNjUGK6OCcThJ9Ap5r9d6qpWovQyCH7J/view?usp=sharing) (Link to private Google Drive).

The database dump can be found [here](https://drive.google.com/file/d/1ESn3K8-WcrAFuK5MoEwTen4mjHfZ_xcC/view?usp=sharing) (Link to private Google Drive).

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
ssh -i "path\to\ssh-key-2025-02-12.key" ubuntu@{bachelor-ip} "docker exec bachelor-mongodb mongodump --db=bachelor --archive --gzip" | docker exec -i bachelor-mongodb mongorestore --archive --gzip --nsInclude='bachelor.*'
```
