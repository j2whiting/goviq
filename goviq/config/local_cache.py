import os
import logging


def get_local_cache_path():
    path = os.getenv('GOVIQ_LOCAL_PATH', '')
    if not path:
        raise RuntimeWarning('GOVIQ_LOCAL_PATH ENV variable not set. Using working directory as default path.')
    else:
        if not os.path.exists(path):
            logging.info(f'Directory not found at {path}. Creating directory.')
            os.makedirs(path)
    return path


LOCAL_CACHE = get_local_cache_path()
