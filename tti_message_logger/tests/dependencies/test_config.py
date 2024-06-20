import pytest
from tti_message_logger.dependencies.config import LoggerConfig, RabbitConfig, MqttConfig


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


@pytest.mark.parametrize(
    "mqtt_host,mqtt_port,mqtt_sensor_data_sub_topic, mqtt_pass",
    [
        ("eu1.cloud.thethings.industries", "1883", "#", "pass_1"),
        ("test.mosquitto.org", "8883", "sensors/#", "pass_2"),
        ("192.168.1.2", "1884", "test/device/sensors", "pass_3"),
    ],
)
def test_mqtt_config(mqtt_host, mqtt_port, mqtt_sensor_data_sub_topic, mqtt_pass):
    config = MqttConfig(
        mqtt_host=mqtt_host,
        mqtt_port=mqtt_port,
        mqtt_sensor_data_sub_topic=mqtt_sensor_data_sub_topic,
        mqtt_pass=mqtt_pass,
    )
    assert config.mqtt_host == mqtt_host
    assert config.mqtt_port == mqtt_port
    assert config.mqtt_sensor_data_sub_topic == mqtt_sensor_data_sub_topic
    assert config.mqtt_pass == mqtt_pass
