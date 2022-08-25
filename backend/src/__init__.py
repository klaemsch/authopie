from pydantic import ValidationError
import sys
from .utils.logger import get_logger, test_logger  # noqa F401
from .utils.config import load_config

# initialze custom logging
logger = get_logger('authopie', 'DEBUG')
# test_logger(logger)

try:
    config = load_config()
except ValidationError as exc:
    logger.warn('Corrupt or Incorrect config file')
    logger.debug(exc)
    sys.exit()
