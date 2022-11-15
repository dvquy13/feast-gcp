import os
import json
import functions_framework
from datetime import datetime

import pandas as pd

from feast.repo_config import RegistryConfig, RepoConfig
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
from feast import FeatureStore
from feast.data_source import PushMode


@functions_framework.http
def feast_process_event(request):
    """Update Feature Store with real-time events

    Args:
        request (HTTP request): containing json event
            request.events is in this format:
            {
                "user_id": "2136639",
                "events": [
                    {
                        "event_name": "Reservation",
                        "merchant_uid": "blukouzina82fps33a-4",
                        "unix_timestamp_seconds_utc": "1664199064"
                    }
                ]
            }
    """
    # decode http request payload and translate into JSON object
    request_str = request.data.decode("utf-8")
    request_json = json.loads(request_str)

    user_id = request_json.get("user_id")
    events = request_json.get("events")

    print(f"Input events: {events}")

    redis_host = os.environ.get("REDIS_HOST")

    repo_config = RepoConfig(
        registry=RegistryConfig(path="gs://feast-gcp-feast/registry.pb"),
        project="feast_gcp",
        provider="gcp",
        # offline_store="bigquery",  # Assume BigQuery is default for provide=gcp
        online_store=RedisOnlineStoreConfig(connection_string=f"{redis_host}:6379"),
        entity_key_serialization_version=2,
    )
    fs = FeatureStore(config=repo_config)

    feature_list = ["dinner_recent_rez:list_10_recent_rez"]
    entity_name_list = ["user_id"]
    entity_value_list = [str(user_id)]
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

    print(f"Feature value retrieved: {online_features}")

    # Update feature value with new event
    current_feature_raw = online_features["list_10_recent_rez"][0]
    current_feature_list = current_feature_raw.split(",")
    print(f"Current Feature List: {current_feature_list}")
    new_feature_list = current_feature_list[:]
    for event in events:
        merchant_uid = event["merchant_uid"]
        timestamp = event["unix_timestamp_seconds_utc"]
        event_str = f"{merchant_uid}_{timestamp}"
        new_feature_list.append(event_str)
    # Truncate to keep only 10 most recent events
    new_feature_list = new_feature_list[-10:]

    # Push new feature value
    feature_df = pd.DataFrame.from_dict(
        {
            "user_id": [user_id],
            "event_timestamp": [datetime.utcnow()],
            "created_timestamp": [datetime.utcnow()],
            "list_10_recent_rez": [",".join(new_feature_list)],
        }
    )

    print("Pushing new feature value to online and offline stores...")
    fs.push(
        "dinner_rez_history_push_source", feature_df, to=PushMode.ONLINE_AND_OFFLINE
    )

    return {"message": "OK"}
