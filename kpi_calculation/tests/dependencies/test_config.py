import pytest
from kpi_calculation.dependencies.config import LoggerConfig


@pytest.mark.parametrize(
    "loglevel,logfile,logger_name",
    [
        ("debug", "./tti_message_logger.log", "tti_message_logger"),
        ("warning", "./my_logger.log", "my_logger"),
        ("error", "./error.log", "error_logger"),
    ],
)
def test_logger_config_kpi_calculation(loglevel, logfile, logger_name):
    config = LoggerConfig(loglevel=loglevel, logfile=logfile, logger_name=logger_name)
    assert config.loglevel == loglevel
    assert config.logfile == logfile
    assert config.logger_name == logger_name