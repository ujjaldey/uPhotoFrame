import logging
import os


def create_logger(file_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s", "%Y-%m-%d %H:%M:%S")

    log_file = _get_log_file_name(file_name)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def _get_log_file_name(file_name):
    path = os.path.dirname(os.path.abspath(file_name))
    log_path = os.path.join(path, "log")
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    return os.path.join(log_path, os.path.basename(file_name).replace(".py", ".log"))

