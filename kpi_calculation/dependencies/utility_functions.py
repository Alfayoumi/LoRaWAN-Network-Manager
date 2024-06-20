from datetime import datetime
from typing import List
import logging
import sys
from logging.handlers import RotatingFileHandler
from .config import LoggerConfig

UPLINK_FREQUENCY_PLAN = {"EU863_870": [868.1, 868.3, 868.5, 867.1, 867.3, 867.5, 867.7, 867.9]}
UPLINK_SF = {"EU863_870": [7, 8, 9, 10, 11, 12]}


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


def get_region_freq_plan(freq: str) -> List[str]:
    region_freq_plan = {
        "EU": [
            "868100000",
            "868300000",
            "868500000",
            "867100000",
            "867300000",
            "867500000",
            "867700000",
            "867900000",
        ],
        "US": [
            "902300000",
            "902500000",
            "902700000",
            "902900000",
            "903100000",
            "903300000",
            "903500000",
            "903700000",
            "903900000",
            "904100000",
            "904300000",
            "904500000",
            "904700000",
            "904900000",
            "905100000",
            "905300000",
        ],
        "AU": [
            "915200000",
            "915400000",
            "915600000",
            "915800000",
            "916000000",
            "916200000",
            "916400000",
            "916600000",
            "916800000",
            "917000000",
            "917200000",
            "917400000",
            "917600000",
            "917800000",
            "918000000",
            "918200000",
        ],
        # Add other regions if needed
    }

    for region, freq_list in region_freq_plan.items():
        if freq in freq_list:
            return freq_list

    # If the frequency is not in any region, return an empty list
    return []


def find_missing(lst):
    return [x for x in range(lst[0], lst[-1] + 1) if x not in lst]


def get_frequency_plan(frequency_plan):
    return UPLINK_FREQUENCY_PLAN[frequency_plan]


def string_to_datetime(s):
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(f"Invalid datetime string: {s}")
