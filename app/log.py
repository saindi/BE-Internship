import os
import logging

current_file = os.path.abspath(__file__)

project_root = os.path.dirname(current_file)

logging_conf_path = os.path.join(project_root, 'logging.conf')

logging.config.fileConfig(logging_conf_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
