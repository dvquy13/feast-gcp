from feast import FeatureStore

from feast_gcp.custom_logging import logger


class FeastWrapper:
    """This class is a wrapper of feast.FeatureStore. It's created to have more control over
    the FeatureStore client, e.g. refresh the repo upon a trigger.
    """

    def __init__(self, repo_path: str, fs_yaml_file: str):
        self.repo_path = repo_path
        self.fs_yaml_file = fs_yaml_file
        self.fs = FeatureStore(repo_path=repo_path, fs_yaml_file=fs_yaml_file)

    def refresh_client(self):
        logger.info("Re-initializing FeatureStore client...")
        self.fs = FeatureStore(repo_path=self.repo_path, fs_yaml_file=self.fs_yaml_file)
