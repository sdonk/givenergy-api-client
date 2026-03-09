"""GivEnergy API Client — Python library for the GivEnergy Cloud API v1."""

from givenergy_api_client.account import Account, AccountData, AccountDevice
from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.communication_device import CommunicationDevice
from givenergy_api_client.ems import EMS, EMSSnapshot
from givenergy_api_client.energy_flow import EnergyDataFlowGrouping, EnergyDataFlowType
from givenergy_api_client.ev_charger import (
    ChargingSession,
    EVCharger,
    EVChargerCommandResult,
    EVChargerData,
    EVChargerMeterReading,
)
from givenergy_api_client.exceptions import (
    APIValidationError,
    AuthenticationError,
    GivEnergyAPIError,
    NotFoundError,
    ServerError,
)
from givenergy_api_client.inverter import DebugCommandResult, EnergyFlowData, Inverter, InverterHealthCheck
from givenergy_api_client.inverter_preset import InverterPreset, InverterPresetData, PresetApplyResult
from givenergy_api_client.pagination import PaginatedResult, PaginationMeta

__all__ = [
    # Client
    "GivenergyAPIClient",
    # Domain classes
    "Account",
    "Inverter",
    "EMS",
    "EVCharger",
    "InverterPreset",
    # Account models
    "AccountData",
    "AccountDevice",
    # Communication device
    "CommunicationDevice",
    # Inverter models
    "InverterHealthCheck",
    "EnergyFlowData",
    "DebugCommandResult",
    # EMS models
    "EMSSnapshot",
    # EV Charger models
    "EVChargerData",
    "EVChargerMeterReading",
    "ChargingSession",
    "EVChargerCommandResult",
    # Inverter preset models
    "InverterPresetData",
    "PresetApplyResult",
    # Pagination
    "PaginatedResult",
    "PaginationMeta",
    # Energy flow enums
    "EnergyDataFlowGrouping",
    "EnergyDataFlowType",
    # Exceptions
    "GivEnergyAPIError",
    "AuthenticationError",
    "NotFoundError",
    "APIValidationError",
    "ServerError",
]
