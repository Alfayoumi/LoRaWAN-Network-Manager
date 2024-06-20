import os


class LoggerConfig:
    def __init__(
        self,
        loglevel: str = os.environ.get("LOG_LEVEL", "debug"),
        logfile: str = os.environ.get("LOG_FILE", "./stream_event_consumer_logger.log"),
        logger_name: str = os.environ.get("LOGGER_NAME", "stream_event_consumer_logger"),
        max_bytes: int = int(os.environ.get("MAX_BYTES", "100000")),
        backup_count: int = int(os.environ.get("BACKUP_COUNT", "10")),
    ) -> None:
        self.loglevel = loglevel
        self.logfile = logfile
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.logger_name = logger_name


class RabbitConfig:
    def __init__(
        self,
        rabbit_username: str = os.environ.get("RABBITMQ_USERNAME"),
        rabbit_password: str = os.environ.get("RABBITMQ_PASSWORD"),
        host_rabbit: str = os.environ.get("RABBITMQ_HOST"),
        queue_name: str = os.environ.get("QUEUE_NAME"),
        routing_key: str = os.environ.get("ROUTING_KEY"),
    ) -> None:
        self.credentials_username = rabbit_username
        self.credentials_password = rabbit_password
        self.host_rabbit = host_rabbit
        self.queue_name = queue_name
        self.routing_key = routing_key


class TOAConfig:
    SYMBOL_DURATION_THRESHOLD = 16
    KHZ_TO_HZ_CONVERTION = 1000
    FIXED_PREAMBLE_DURATION = 4.25  # IN SEC
    PAYLOAD_CRC_LENGTH = 16
    SF_LENGTH = 4
    CR_LENGTH = 4
    HEADER_PLUS_CRC_LENGTH = 20
    FROM_BYTE_TO_BITS = 8


kpi_calculation_config = TOAConfig()
logger_config = LoggerConfig()
rabbit_config = RabbitConfig()
