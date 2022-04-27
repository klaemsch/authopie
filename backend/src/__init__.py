from pydantic import ValidationError
import sys
import logging


try:
    from .config import config  # noqa F401
    # TODO: create own logger
    logger = logging.getLogger('my_logger')
except ValidationError:
    logger = logging.getLogger('uvicorn.error')
    logger.warn('Corrupt or Incorrect config file')
    sys.exit()
