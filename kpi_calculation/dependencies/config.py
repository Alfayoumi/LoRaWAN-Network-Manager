class LoggerConfig:
    def __init__(
        self,
        loglevel: str = "debug",
        logfile: str = "./kpi_calculation.log",
        logger_name: str = "kpi_calculation",
        max_bytes: int = 100000,
        backup_count: int = 10,
    ) -> None:
        self.loglevel = loglevel
        self.logfile = logfile
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.logger_name = logger_name


class KPIConfig:
    SYMBOL_DURATION_THRESHOLD = 16
    KHZ_TO_HZ_CONVERTION = 1000
    FIXED_PREAMBLE_DURATION = 4.25  # IN SEC
    PAYLOAD_CRC_LENGTH = 16
    SF_LENGTH = 4
    CR_LENGTH = 4
    HEADER_PLUS_CRC_LENGTH = 20
    FROM_BYTE_TO_BITS = 8


logger_config = LoggerConfig()
kpi_calculation_config = KPIConfig()
