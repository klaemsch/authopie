from logging import Formatter, getLogger
from logging import Logger, StreamHandler
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class DefaultFormatter(Formatter):
    """Custom logger
    - Color changes based on logging level
    - prints file the log originated from
    - prints severity level
    """

    # https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters
    BLUE = "\x1b[34;22m"
    GREEN = "\x1b[32;22m"
    YELLOW = "\x1b[33;22m"
    RED = "\x1b[31;22m"
    BOLD_RED = "\x1b[31;1m"

    MAGENTA = "\x1b[35;22m"
    CYAN = "\x1b[36;22m"
    WHITE = "\x1b[37;22m"
    DEFAULT = "\x1b[39;22m"

    RESET = "\x1b[0m"

    # logging format
    FORM = "%(asctime)s - %(name)s [%(levelname)s]: %(message)s (%(filename)s:%(lineno)d)"

    # combines color, logging format and reset
    FORMATS = {
        DEBUG: BLUE + FORM + RESET,
        INFO: GREEN + FORM + RESET,
        WARNING: YELLOW + FORM + RESET,
        ERROR: RED + FORM + RESET,
        CRITICAL: BOLD_RED + FORM + RESET
    }

    def format(self, record):
        """custom format. calls default format method"""

        # generate logging format string
        log_fmt = self.FORMATS.get(record.levelno)

        # get default logging formatter with new date format
        formatter = Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")

        # call default formatter
        return formatter.format(record)


def get_logger(name: str, level: int | str) -> Logger:
    """Configures logging"""

    # create logger
    logger = getLogger(name)

    # set logging level
    logger.setLevel(level)

    # create handler that prints to console
    handler = StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(DefaultFormatter())

    # add handler to logger
    logger.addHandler(handler)

    return logger


def test_logger(logger: Logger) -> None:
    """tests logging output"""
    logger.debug('This is the debug logger')
    logger.info('This is the info logger')
    logger.warning('This is the warn logger')
    logger.error('This is the error logger')
    logger.critical('This is the critical logger')
