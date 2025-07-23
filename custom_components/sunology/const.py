""" Sunology const file """
from enum import StrEnum

DOMAIN = "sunology"

CONF_GATEWAY_HOST = "lan_gateway_host"
CONF_GATEWAY_PORT = "lan_gateway_port"

MIN_UNTIL_REFRESH = 2

PACKAGE_NAME = f"custom_components.{DOMAIN}"


class SmartMeterPhase(StrEnum):
    """Phase of a smart meter."""
    ALL = "All"
    PHASE_1 = "P1"
    PHASE_2 = "P2"
    PHASE_3 = "P3"

class SmartMeterTarifIndex(StrEnum):
    """Phase of a smart meter."""
    INDEX_1 = "idx1"
    INDEX_2 = "idx2"
    INDEX_3 = "idx3"
    INDEX_4 = "idx4"
    INDEX_5 = "idx5"
    INDEX_6 = "idx6"
    INDEX_7 = "idx7"
    INDEX_8 = "idx8"
    INDEX_9 = "idx9"
    INDEX_10 = "idx10"
