""" Sunology const file """
from enum import StrEnum

DOMAIN = "sunology"

CONF_GATEWAY_IP = "lan_gateway_ip"

MIN_UNTIL_REFRESH = 2

PACKAGE_NAME = f"custom_components.{DOMAIN}"


class SmartMeterPhase(StrEnum):
    """Phase of a smart meter."""
    ALL = "All"
    PHASE_1 = "P1"
    PHASE_2 = "P2"
    PHASE_3 = "P3"
