.PHONY: build up down import test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down -v

import:
	docker cp data/avis_sample.json mongo_service:/tmp/avis_sample.json && \
	docker exec -it mongo_service bash -lc "mongoimport --db satisfaction --collection avis --jsonArray --drop --file /tmp/avis_sample.json"

test:
	curl http://localhost:8000/avis || true
