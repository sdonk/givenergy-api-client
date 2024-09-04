import datetime as dt
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, PositiveFloat, PositiveInt


class InverterStatus(Enum):
    NORMAL = "NORMAL"
    ERROR = "ERROR"
    LOST = "LOST"
    WAITING = "WAITING"


class BatteryType(Enum):
    LITHIUM = "LITHIUM"


class BatteryInfo(BaseModel):
    nominal_capacity: PositiveInt
    nominal_voltage: PositiveFloat
    depth_of_discharge: PositiveInt
    model_config = ConfigDict(frozen=True)


class Battery(BaseModel):
    battery_type: BatteryType
    battery: BatteryInfo
    model: str
    max_charge_rate: int
    model_config = ConfigDict(frozen=True)


class WarrantyType(Enum):
    Standard = "Standard"


class Warranty(BaseModel):
    type: WarrantyType
    expiry_date: dt.datetime
    model_config = ConfigDict(frozen=True)


class FirmwareVersion(BaseModel):
    ARM: PositiveInt
    DSP: PositiveInt
    model_config = ConfigDict(frozen=True)


class ConnectionBatteryCapacity(BaseModel):
    full: PositiveInt
    design: PositiveInt
    model_config = ConfigDict(frozen=True)


class ConnectionBattery(BaseModel):
    module_number: PositiveInt
    serial: str
    firmware_version: int
    capacity: ConnectionBatteryCapacity
    cell_count: PositiveInt
    has_usb: bool
    nominal_voltage: PositiveFloat
    model_config = ConfigDict(frozen=True)


class ConnectionMeter(BaseModel):
    address: PositiveInt
    serial_number: PositiveInt
    manufacturer_code: str
    type_code: PositiveInt
    hardware_version: PositiveInt
    software_version: PositiveInt
    baud_rate: PositiveInt
    model_config = ConfigDict(frozen=True)


class Connections(BaseModel):
    batteries: List[ConnectionBattery]
    meters: List[ConnectionMeter]
    model_config = ConfigDict(frozen=True)


class Inverter(BaseModel):
    serial: str
    status: InverterStatus
    last_online: dt.datetime
    last_updated: dt.datetime
    commission_date: dt.datetime
    info: Battery
    warranty: Warranty
    firmware_version: FirmwareVersion
    connections: Connections
    flags: List[Optional[str]]

    model_config = ConfigDict(frozen=True)


class CommunicationDevice(BaseModel):
    serial_number: str
    firmware_version: int
    type: str
    commission_date: dt.datetime
    inverter: Inverter

    model_config = ConfigDict(frozen=True)
