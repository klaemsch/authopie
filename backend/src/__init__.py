from pydantic import ValidationError
import sys
from src.util import get_logger, test_logger

# initialze custom logging
logger = get_logger('authopie', 'DEBUG')
test_logger(logger)

try:
    from .config import config  # noqa:F401
except ValidationError:
    logger.warn('Corrupt or Incorrect config file')
    sys.exit()
