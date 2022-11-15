from feast import FeatureService

from entities.dinner.recent_rez import dinner_recent_rez_fv


seq_rec_fs = FeatureService(
    name="seq_rec",
    features=[dinner_recent_rez_fv],
    tags={"used_in": "seq_rec"},
    owner="dvquy.13@gmail.com",
)
