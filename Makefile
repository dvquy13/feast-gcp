plan:
	cd feature_repo && \
	poetry run feast plan

lab:
	poetry run jupyter lab

build:
	gcloud builds submit \
		--config cloudbuild.yaml \
		--timeout 3600s \
		.

up-db:
	docker-compose -f feature_repo/local/docker-compose.yml up -d

down-db:
	docker-compose -f feature_repo/local/docker-compose.yml down

up-svc:
	export ENV=local && \
	poetry run uvicorn main:app --host=0.0.0.0 --port=8080 --reload
