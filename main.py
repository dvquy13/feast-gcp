import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from feast import FeatureStore

from feast_gcp.utils import run_cli_cmd, get_feast_cmd_by_env

import logging

logging.getLogger("feast_gcp").setLevel(logging.DEBUG)
from feast_gcp.custom_logging import (
    logger,
    logging_request_uuid,
)

env = os.environ.get("ENV", "prod")
logger.info(f"ENV: {env}")

app = FastAPI()


@app.get("/")
def read_root():
    url = "/docs"
    response = RedirectResponse(url=url, status_code=303)
    return response


@app.get("/feast/materialize")
def materialize(
    start_ts: str = "2022-09-13T00:00:00",
    end_ts: str = "2022-09-16T00:00:00",
):
    """Build selected models

    Args:
        start_ts (str): ISO format start datetime. Default originates from the demo recent_rez dataset.
        end_ts (str): ISO format start datetime. Default originates from the demo recent_rez dataset.

    Returns:
        dict: command output message
    """
    base_cmd = get_feast_cmd_by_env(env)
    cmd = ["materialize", start_ts, end_ts]
    full_cmd = base_cmd + cmd
    cwd_dir = "feature_repo"
    logger.info(f"Running CMD {full_cmd} from directory {cwd_dir}...")
    cmd_exit_code = run_cli_cmd(full_cmd, cwd=cwd_dir)

    return {
        "message": "Build complete! Please check server log for more info.",
        "exit_code": cmd_exit_code,
    }


@logging_request_uuid
@app.get("/test_redis_connection")
def test_redis_connection(host: str, port: str):
    import redis

    logger.debug("Initializing Redis Client...")
    r = redis.Redis(host=host, port=port)
    return {"r.ping": r.ping()}


@app.get("/test_gcs_connection")
def test_redis_connection(bucket_name: str = "feast-gcp-feast"):
    from google.cloud import storage

    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)

    blobs = []
    for blob in bucket.list_blobs():
        blobs.append(blob.name)

    return {"blobs": blobs}


@app.get("/test_online_store")
def test_online_store(
    features: str = "dinner_recent_rez:list_10_recent_rez",
    entity_name: str = "user_id",
    entity_value: str = "2136639",
):
    """Test retrieving features from online store

    Args:
        features (str, optional): Features to retrieve, comma delimited. Defaults to "dinner_recent_rez:list_10_recent_rez".
        entity_name (str, optional): The entity to retrieve, comma delimited. Defaults to "user_id".
        entity_value (str, optional): The entity value to retrieve, comma delimited. Defaults to "2136639".

    Returns:
        dict: feature values
    """
    fs_yaml_file_path = f"feature_repo/{env}/feature_store.yaml"
    logger.info(f"Initializing FeatureStore from {fs_yaml_file_path}...")
    fs = FeatureStore(repo_path="feature_repo/", fs_yaml_file=fs_yaml_file_path)

    feature_list = features.split(",")
    entity_name_list = entity_name.split(",")
    entity_value_list = entity_value.split(",")
    if len(entity_name_list) != len(entity_value_list):
        return {
            "message": "entity_name and entity_value do not have same length!",
            "result": [],
        }
    entity_rows = []
    for i in range(len(entity_name_list)):
        entity_rows.append({entity_name_list[i]: entity_value_list[i]})

    online_features = fs.get_online_features(
        features=feature_list,
        entity_rows=entity_rows,
    ).to_dict()

    return {"message": "OK", "result": online_features}


@app.get("/feast/cli")
def feast_cli(cmd: str):
    base_cmd = get_feast_cmd_by_env(env)
    cmd = [cmd]
    full_cmd = base_cmd + cmd
    cwd_dir = "feature_repo"
    logger.info(f"Running CMD {full_cmd} from directory {cwd_dir}...")
    cmd_exit_code = run_cli_cmd(full_cmd, cwd=cwd_dir)

    return {
        "message": f"CMD `{' '.join(full_cmd)}` complete! Please check server log for more info.",
        "exit_code": cmd_exit_code,
    }
