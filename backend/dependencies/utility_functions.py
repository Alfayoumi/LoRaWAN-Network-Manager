import logging
import sys
from logging.handlers import RotatingFileHandler
from .config import LoggerConfig


def get_logger(logger_config: LoggerConfig) -> logging.Logger:
    """
    Set up a logger according to the specified configuration settings.

    Args:
        logger_config (LoggerConfig): An instance of LoggerConfig class that contains
        the logger configuration settings.

    Returns:
        logging.Logger: A new logger object.

    Raises:
        ValueError: If an invalid log level is specified in the configuration settings.
        IOError: If there is a problem with the log file.
    """

    # Create logger object
    logger = logging.getLogger(logger_config.logger_name)

    # Set logger level
    numeric_level = getattr(logging, logger_config.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {logger_config.loglevel}")
    logger.setLevel(numeric_level)

    # Configure log file handler
    try:
        log_handler = RotatingFileHandler(
            filename=logger_config.logfile,
            maxBytes=logger_config.max_bytes,
            backupCount=logger_config.backup_count,
        )
    except IOError as e:
        raise IOError(f"Error opening log file: {e}")
    log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))
    logger.addHandler(log_handler)

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

    return logger
