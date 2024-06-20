import pytest
from apicelery.dependencies.config import LoggerConfig, RabbitConfig


@pytest.mark.parametrize(
    "loglevel,logfile,logger_name",
    [
        ("debug", "./apicelery_logger.log", "apicelery_logger"),
        ("warning", "./my_logger.log", "my_logger"),
        ("error", "./error.log", "error_logger"),
    ],
)
def test_logger_config(loglevel, logfile, logger_name):
    config = LoggerConfig(loglevel=loglevel, logfile=logfile, logger_name=logger_name)
    assert config.loglevel == loglevel
    assert config.logfile == logfile
    assert config.logger_name == logger_name
