import base64
import math
import logging
import sys
from logging.handlers import RotatingFileHandler
from .config import LoggerConfig
from .config import kpi_calculation_config
from .exceptions import CalculationError


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


def get_payload_size(frm_payload: str) -> int:
    """
    Returns the size of the physical layer payload (PHY payload) of the LoRaWAN packet
    with the given frame payload.
    """
    decoded_payload = base64.b64decode(frm_payload)
    return len(decoded_payload)


def calculate_toa(
        n_size,
        n_sf,
        n_bw=125.0,
        enable_auto_ldro=True,
        enable_ldro=False,
        enable_eh=True,
        enable_crc=True,
        n_cr=1,
        n_preamble=8,
):
    try:
        if not isinstance(n_size, int) or not isinstance(n_sf, int):
            raise CalculationError(f"Invalid input. {n_size}  and {n_sf}  must be integers.")
        if n_size <= 0 or n_sf <= 0:
            raise CalculationError(f"Invalid input. {n_size}  and {n_sf} must be positive integers.")

        r_sym = (n_bw * kpi_calculation_config.KHZ_TO_HZ_CONVERTION) / math.pow(2, n_sf)
        t_sym = kpi_calculation_config.KHZ_TO_HZ_CONVERTION / r_sym
        t_preamble = (n_preamble + kpi_calculation_config.FIXED_PREAMBLE_DURATION) * t_sym

        v_de = 0
        if (
                enable_auto_ldro
                and t_sym > kpi_calculation_config.SYMBOL_DURATION_THRESHOLD
                or not enable_auto_ldro
                and enable_ldro
        ):
            v_de = 1

        v_ih = 0
        if not enable_eh:
            v_ih = 1

        v_crc = 1
        if not enable_crc:
            v_crc = 0

        numerator = (
                kpi_calculation_config.FROM_BYTE_TO_BITS * n_size
                - kpi_calculation_config.SF_LENGTH * n_sf
                + 28
                + kpi_calculation_config.PAYLOAD_CRC_LENGTH * v_crc
                - kpi_calculation_config.HEADER_PLUS_CRC_LENGTH * v_ih
        )
        denominator = kpi_calculation_config.SF_LENGTH * (n_sf - 2.0 * v_de)
        n_payload = 8 + max(
            math.ceil(numerator / denominator) * (n_cr + kpi_calculation_config.CR_LENGTH), 0
        )
        t_payload = n_payload * t_sym
        t_packet = t_preamble + t_payload

        return {"t_payload": t_payload, "t_packet": round(t_packet, 3)}
    except Exception as e:
        raise CalculationError(f"Error in TOA calculation: {str(e)}")
