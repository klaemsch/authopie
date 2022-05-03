from pydantic import ValidationError
import sys
from .util import get_logger, test_logger, load_config

# initialze custom logging
logger = get_logger('authopie', 'DEBUG')
test_logger(logger)

try:
    config = load_config()
except ValidationError:
    logger.warn('Corrupt or Incorrect config file')
    sys.exit()
