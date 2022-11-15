from feast import Entity

dinner = Entity(
    name="dinner",
    join_keys=["user_id"],
)
