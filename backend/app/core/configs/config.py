import logging
import os
import sys

from dotenv import load_dotenv
from pydantic import ValidationError

from app.core.configs.env_configs_models import SettingsModel

logger = logging.getLogger(__name__)

try:
    settings = SettingsModel(**os.environ)
except ValidationError:
    load_dotenv()
    try:
        settings = SettingsModel(**os.environ)
    except ValidationError as e:
        logger.critical(exc_info=e, msg="Settings validation")
        sys.exit(-1)

# if settings.IS_DEBUG:
#     root_logger.setLevel(logging.DEBUG)
# else:
#     root_logger.setLevel(logging.INFO)
