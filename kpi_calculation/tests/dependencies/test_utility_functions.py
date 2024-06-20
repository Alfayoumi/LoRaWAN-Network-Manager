import pytest
from kpi_calculation.dependencies.utility_functions import get_logger, LoggerConfig
import logging


@pytest.mark.parametrize(
    "config",
    [
        LoggerConfig(
            loglevel="debug",
            logfile="./tti_message_logger.log",
            logger_name="tti_message_logger",
            max_bytes=100000,
            backup_count=10,
        ),
        LoggerConfig(
            loglevel="debug",
            logfile="./test.log",
            logger_name="test_logger",
            max_bytes=10000,
            backup_count=5,
        ),
    ],
)
def test_get_logger_kpi_calculation(config):
    logger = get_logger(config)

    # check if the logger object is created successfully
    assert isinstance(logger, logging.Logger)

    # check if the logger level is set correctly
    assert logger.level == getattr(logging, config.loglevel.upper())

    # check if the logger name is set correctly
    assert logger.name == config.logger_name