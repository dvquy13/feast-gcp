# Feast GCP Set up

This project is to set up the Feast Feature Store framework with GCP deployment.

# Set up GCP project
- Create a Service Account for Terraform: `gcloud iam service-accounts create feast-sa --display-name "Terraform and GitHub CI account"`
- Grant SA access to project: `gcloud projects add-iam-policy-binding feast-gcp-project-id --member serviceAccount:feast-sa@feast-gcp-project-id.iam.gserviceaccount.com --role roles/editor`
- Generate SA keys: `gcloud iam service-accounts keys create ~/.config/gcloud/feast-sa-feast-gcp-project-id.json --iam-account feast-sa@feast-gcp-project-id.iam.gserviceaccount.com`
- Register SA as default credentials in your local machine: `export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/feast-sa-feast-gcp-project-id.json`

# Github CI/CD
- Copy the json text of the SA key above and store its as GCP_SA_KEY secret variable on Github repo
- Set secret value for GCP_PROJECT_ID in your Github repo

# Set up Cloud Run to host the Feast Repo
- Enable Cloud Build Service and wait 10 minutes
## Deploy
- Specify the the VERSION input in variables.tf, resource: `main_image_version`
- Paste that VERSION in .github/workflows/plan CLOUD_RUN_MAIN_IMAGE env

# Cloud Functions for Push Event Update
## Local Development
Set up the functions framework at local
```
cd cloud_fn/
export REDIS_HOST=local
poetry run functions-framework --target=feast_process_event --port=8083 --signature-type=http
```

Local calling
```
curl -X POST http://localhost:8083 -H 'Content-Type: application/json' -d '{"user_id": "2136639"}'
```

# References
- Feast Workshop Module 0: https://github.com/feast-dev/feast-workshop/blob/main/module_0/README.md
