import os

from jrnl.exception import JrnlException
from jrnl.path import get_config_directory, home_dir

DEFAULT_CONFIG_NAME = 'jrnl_search_config.yaml'


def get_config_path():
    try:
        config_directory_path = get_config_directory()
    except JrnlException:
        return os.path.join(home_dir(), DEFAULT_CONFIG_NAME)
    return os.path.join(config_directory_path, DEFAULT_CONFIG_NAME)
