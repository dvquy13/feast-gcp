from datetime import timedelta

from feast import BigQuerySource, FeatureView, Field, PushSource
from feast.types import String

from entities.dinner.entity import dinner

dinner_recent_rez_source = BigQuerySource(
    name="dinner_rez_history_source",
    table="feast-gcp-project-id.feast_demo.fct_featurestore_dinner_recent_rez_history",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
    tags={"used_in": "seq_rec"},
    owner="dvquy.13@gmail.com",
)

dinner_recent_rez_push_source = PushSource(
    name="dinner_rez_history_push_source",
    batch_source=dinner_recent_rez_source,
    tags={"used_in": "seq_rec"},
    owner="dvquy.13@gmail.com",
)

dinner_recent_rez_fv = FeatureView(
    name="dinner_recent_rez",
    entities=[dinner],
    ttl=timedelta(weeks=52),
    schema=[
        Field(name="list_10_recent_rez", dtype=String),
    ],
    source=dinner_recent_rez_push_source,
    tags={"used_in": "seq_rec"},
    owner="dvquy.13@gmail.com",
    description="List of 10 recent reservations plus timestamp of users",
)
