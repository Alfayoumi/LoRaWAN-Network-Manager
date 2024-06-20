import pytest
from stream_event_logger.dependencies.config import LoggerConfig, RabbitConfig


@pytest.mark.parametrize(
    "loglevel,logfile,logger_name",
    [
        ("debug", "./tti_message_logger.log", "tti_message_logger"),
        ("warning", "./my_logger.log", "my_logger"),
        ("error", "./error.log", "error_logger"),
    ],
)
def test_logger_config(loglevel, logfile, logger_name):
    config = LoggerConfig(loglevel=loglevel, logfile=logfile, logger_name=logger_name)
    assert config.loglevel == loglevel
    assert config.logfile == logfile
    assert config.logger_name == logger_name


@pytest.mark.parametrize(
    "rabbit_username,rabbit_password,host_rabbit",
    [
        ("user_metadata", "user_metadata", "rabbitmq"),
        ("guest", "guest", "localhost"),
        ("admin", "password", "my_rabbit_server"),
    ],
)
def test_rabbit_config(rabbit_username, rabbit_password, host_rabbit):
    config = RabbitConfig(
        rabbit_username=rabbit_username,
        rabbit_password=rabbit_password,
        host_rabbit=host_rabbit,
    )
    assert config.credentials_username == rabbit_username
    assert config.credentials_password == rabbit_password
    assert config.host_rabbit == host_rabbit