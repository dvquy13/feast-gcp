import subprocess
import sys


def run_cli_cmd(cmd, **kwargs):
    """Run CLI command via Python and print the stdout to console

    Args:
        cmd (str or list)
    """
    # Stream command stdout
    # Ref: https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
    with open("build.log", "wb") as f:
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        process = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, **kwargs
        )
        for line in iter(process.stdout.readline, b""):
            line_decode = line.decode(sys.stdout.encoding)
            sys.stdout.write(line_decode)
            f.write(line)
        process.communicate()
    return process.returncode


def get_feast_cmd_by_env(env: str) -> list:
    """Get feast CLI command by pointing to the feature_store.yaml file corresponding to that env

    Args:
        env (str): environment name. {local, dev, prod}

    Returns:
        list[str]
    """
    cmd = ["feast", "--feature-store-yaml", f"{env}/feature_store.yaml"]
    return cmd
