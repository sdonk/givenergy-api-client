import datetime as dt

import pytest
from pydantic import ValidationError

from givenergy_api_client.communication_device import (
    Battery,
    BatteryInfo,
    BatteryType,
    CommunicationDevice,
    ConnectionBattery,
    ConnectionBatteryCapacity,
    ConnectionMeter,
    Connections,
    FirmwareVersion,
    Inverter,
    InverterStatus,
    Warranty,
    WarrantyType,
)

# ---------------------------------------------------------------------------
# Shared valid payloads
# ---------------------------------------------------------------------------

VALID_BATTERY_INFO = {"nominal_capacity": 110, "nominal_voltage": 51.2, "depth_of_discharge": 1}

VALID_BATTERY = {
    "battery_type": "LITHIUM",
    "battery": VALID_BATTERY_INFO,
    "model": "GIV-AC-3.0",
    "max_charge_rate": 2560,
}

VALID_WARRANTY = {"type": "Standard", "expiry_date": "2033-01-01T00:00:00Z"}

VALID_FIRMWARE_VERSION = {"ARM": 420, "DSP": 426}

VALID_CONNECTION_BATTERY_CAPACITY = {"full": 110, "design": 110}

VALID_CONNECTION_BATTERY = {
    "module_number": 1,
    "serial": "BB2345G123",
    "firmware_version": 1035,
    "capacity": VALID_CONNECTION_BATTERY_CAPACITY,
    "cell_count": 16,
    "has_usb": True,
    "nominal_voltage": 51.2,
}

VALID_CONNECTION_METER = {
    "address": 1,
    "serial_number": 212345678,
    "manufacturer_code": "0000",
    "type_code": 1500,
    "hardware_version": 1000,
    "software_version": 1000,
    "baud_rate": 9600,
}

VALID_CONNECTIONS = {
    "batteries": [VALID_CONNECTION_BATTERY],
    "meters": [VALID_CONNECTION_METER],
}

VALID_INVERTER = {
    "serial": "CE2345G123",
    "status": "WAITING",
    "last_online": "2023-01-01T00:00:00Z",
    "last_updated": "2023-01-01T00:00:00Z",
    "commission_date": "2021-01-01T00:00:00Z",
    "info": VALID_BATTERY,
    "warranty": VALID_WARRANTY,
    "firmware_version": VALID_FIRMWARE_VERSION,
    "connections": VALID_CONNECTIONS,
    "flags": [],
}

VALID_COMMUNICATION_DEVICE = {
    "serial_number": "WF2345G123",
    "type": "WIFI",
    "firmware_version": 123,
    "commission_date": "2021-01-01T00:00:00Z",
    "inverter": VALID_INVERTER,
}


# ---------------------------------------------------------------------------
# InverterStatus enum
# ---------------------------------------------------------------------------


class TestInverterStatus:

    def test_all_values(self) -> None:
        assert InverterStatus.NORMAL.value == "NORMAL"
        assert InverterStatus.ERROR.value == "ERROR"
        assert InverterStatus.LOST.value == "LOST"
        assert InverterStatus.WAITING.value == "WAITING"

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            InverterStatus("UNKNOWN")


# ---------------------------------------------------------------------------
# BatteryType enum
# ---------------------------------------------------------------------------


class TestBatteryType:

    def test_lithium_value(self) -> None:
        assert BatteryType.LITHIUM.value == "LITHIUM"

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            BatteryType("NICKEL")


# ---------------------------------------------------------------------------
# WarrantyType enum
# ---------------------------------------------------------------------------


class TestWarrantyType:

    def test_standard_value(self) -> None:
        assert WarrantyType.Standard.value == "Standard"

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            WarrantyType("Extended")


# ---------------------------------------------------------------------------
# BatteryInfo model
# ---------------------------------------------------------------------------


class TestBatteryInfo:

    def test_valid_construction(self) -> None:
        info = BatteryInfo.model_validate(VALID_BATTERY_INFO)
        assert info.nominal_capacity == 110
        assert info.nominal_voltage == 51.2
        assert info.depth_of_discharge == 1

    def test_is_immutable(self) -> None:
        info = BatteryInfo.model_validate(VALID_BATTERY_INFO)
        with pytest.raises(ValidationError):
            info.nominal_capacity = 999  # type: ignore[misc]

    def test_zero_nominal_capacity_raises(self) -> None:
        with pytest.raises(ValidationError):
            BatteryInfo.model_validate({**VALID_BATTERY_INFO, "nominal_capacity": 0})

    def test_negative_nominal_capacity_raises(self) -> None:
        with pytest.raises(ValidationError):
            BatteryInfo.model_validate({**VALID_BATTERY_INFO, "nominal_capacity": -1})

    def test_zero_nominal_voltage_raises(self) -> None:
        with pytest.raises(ValidationError):
            BatteryInfo.model_validate({**VALID_BATTERY_INFO, "nominal_voltage": 0.0})

    def test_negative_nominal_voltage_raises(self) -> None:
        with pytest.raises(ValidationError):
            BatteryInfo.model_validate({**VALID_BATTERY_INFO, "nominal_voltage": -10.0})

    def test_zero_depth_of_discharge_raises(self) -> None:
        with pytest.raises(ValidationError):
            BatteryInfo.model_validate({**VALID_BATTERY_INFO, "depth_of_discharge": 0})


# ---------------------------------------------------------------------------
# Battery model
# ---------------------------------------------------------------------------


class TestBattery:

    def test_valid_construction(self) -> None:
        battery = Battery.model_validate(VALID_BATTERY)
        assert battery.battery_type == BatteryType.LITHIUM
        assert battery.model == "GIV-AC-3.0"
        assert battery.max_charge_rate == 2560
        assert battery.battery.nominal_capacity == 110

    def test_invalid_battery_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            Battery.model_validate({**VALID_BATTERY, "battery_type": "NICKEL"})

    def test_is_immutable(self) -> None:
        battery = Battery.model_validate(VALID_BATTERY)
        with pytest.raises(ValidationError):
            battery.model = "OTHER"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Warranty model
# ---------------------------------------------------------------------------


class TestWarranty:

    def test_valid_construction(self) -> None:
        warranty = Warranty.model_validate(VALID_WARRANTY)
        assert warranty.type == WarrantyType.Standard
        assert warranty.expiry_date == dt.datetime(2033, 1, 1, tzinfo=dt.timezone.utc)

    def test_invalid_warranty_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            Warranty.model_validate({**VALID_WARRANTY, "type": "Lifetime"})

    def test_invalid_date_raises(self) -> None:
        with pytest.raises(ValidationError):
            Warranty.model_validate({**VALID_WARRANTY, "expiry_date": "not-a-date"})


# ---------------------------------------------------------------------------
# FirmwareVersion model
# ---------------------------------------------------------------------------


class TestFirmwareVersion:

    def test_valid_construction(self) -> None:
        fw = FirmwareVersion.model_validate(VALID_FIRMWARE_VERSION)
        assert fw.ARM == 420
        assert fw.DSP == 426

    def test_zero_arm_raises(self) -> None:
        with pytest.raises(ValidationError):
            FirmwareVersion.model_validate({"ARM": 0, "DSP": 426})

    def test_negative_dsp_raises(self) -> None:
        with pytest.raises(ValidationError):
            FirmwareVersion.model_validate({"ARM": 420, "DSP": -1})


# ---------------------------------------------------------------------------
# ConnectionBatteryCapacity model
# ---------------------------------------------------------------------------


class TestConnectionBatteryCapacity:

    def test_valid_construction(self) -> None:
        cap = ConnectionBatteryCapacity.model_validate(VALID_CONNECTION_BATTERY_CAPACITY)
        assert cap.full == 110
        assert cap.design == 110

    def test_zero_full_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionBatteryCapacity.model_validate({"full": 0, "design": 110})

    def test_zero_design_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionBatteryCapacity.model_validate({"full": 110, "design": 0})


# ---------------------------------------------------------------------------
# ConnectionBattery model
# ---------------------------------------------------------------------------


class TestConnectionBattery:

    def test_valid_construction(self) -> None:
        bat = ConnectionBattery.model_validate(VALID_CONNECTION_BATTERY)
        assert bat.serial == "BB2345G123"
        assert bat.module_number == 1
        assert bat.cell_count == 16
        assert bat.has_usb is True
        assert bat.nominal_voltage == 51.2
        assert bat.capacity.full == 110

    def test_zero_module_number_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionBattery.model_validate({**VALID_CONNECTION_BATTERY, "module_number": 0})

    def test_negative_nominal_voltage_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionBattery.model_validate({**VALID_CONNECTION_BATTERY, "nominal_voltage": -1.0})

    def test_is_immutable(self) -> None:
        bat = ConnectionBattery.model_validate(VALID_CONNECTION_BATTERY)
        with pytest.raises(ValidationError):
            bat.serial = "OTHER"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ConnectionMeter model
# ---------------------------------------------------------------------------


class TestConnectionMeter:

    def test_valid_construction(self) -> None:
        meter = ConnectionMeter.model_validate(VALID_CONNECTION_METER)
        assert meter.address == 1
        assert meter.serial_number == 212345678
        assert meter.manufacturer_code == "0000"
        assert meter.type_code == 1500
        assert meter.hardware_version == 1000
        assert meter.software_version == 1000
        assert meter.baud_rate == 9600

    def test_zero_address_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionMeter.model_validate({**VALID_CONNECTION_METER, "address": 0})

    def test_zero_baud_rate_raises(self) -> None:
        with pytest.raises(ValidationError):
            ConnectionMeter.model_validate({**VALID_CONNECTION_METER, "baud_rate": 0})


# ---------------------------------------------------------------------------
# Connections model
# ---------------------------------------------------------------------------


class TestConnections:

    def test_valid_construction(self) -> None:
        conn = Connections.model_validate(VALID_CONNECTIONS)
        assert len(conn.batteries) == 1
        assert len(conn.meters) == 1

    def test_empty_batteries_and_meters(self) -> None:
        conn = Connections.model_validate({"batteries": [], "meters": []})
        assert conn.batteries == []
        assert conn.meters == []

    def test_multiple_batteries(self) -> None:
        second_battery = {**VALID_CONNECTION_BATTERY, "module_number": 2, "serial": "BB9999X999"}
        conn = Connections.model_validate({"batteries": [VALID_CONNECTION_BATTERY, second_battery], "meters": []})
        assert len(conn.batteries) == 2


# ---------------------------------------------------------------------------
# Inverter model
# ---------------------------------------------------------------------------


class TestInverter:

    def test_valid_construction(self) -> None:
        inverter = Inverter.model_validate(VALID_INVERTER)
        assert inverter.serial == "CE2345G123"
        assert inverter.status == InverterStatus.WAITING
        assert inverter.last_online == dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
        assert inverter.last_updated == dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
        assert inverter.commission_date == dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)
        assert inverter.flags == []

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValidationError):
            Inverter.model_validate({**VALID_INVERTER, "status": "CHARGING"})

    def test_all_inverter_statuses_accepted(self) -> None:
        for status in ("NORMAL", "ERROR", "LOST", "WAITING"):
            inverter = Inverter.model_validate({**VALID_INVERTER, "status": status})
            assert inverter.status == InverterStatus(status)

    def test_is_immutable(self) -> None:
        inverter = Inverter.model_validate(VALID_INVERTER)
        with pytest.raises(ValidationError):
            inverter.serial = "OTHER"  # type: ignore[misc]

    def test_flags_can_contain_strings(self) -> None:
        inverter = Inverter.model_validate({**VALID_INVERTER, "flags": ["FLAG_A", "FLAG_B"]})
        assert inverter.flags == ["FLAG_A", "FLAG_B"]


# ---------------------------------------------------------------------------
# CommunicationDevice model
# ---------------------------------------------------------------------------


class TestCommunicationDevice:

    def test_valid_construction(self) -> None:
        device = CommunicationDevice.model_validate(VALID_COMMUNICATION_DEVICE)
        assert device.serial_number == "WF2345G123"
        assert device.firmware_version == 123
        assert device.type == "WIFI"
        assert device.commission_date == dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)
        assert device.inverter.serial == "CE2345G123"

    def test_missing_inverter_raises(self) -> None:
        incomplete = {k: v for k, v in VALID_COMMUNICATION_DEVICE.items() if k != "inverter"}
        with pytest.raises(ValidationError):
            CommunicationDevice.model_validate(incomplete)

    def test_is_immutable(self) -> None:
        device = CommunicationDevice.model_validate(VALID_COMMUNICATION_DEVICE)
        with pytest.raises(ValidationError):
            device.serial_number = "OTHER"  # type: ignore[misc]

    def test_invalid_commission_date_raises(self) -> None:
        with pytest.raises(ValidationError):
            CommunicationDevice.model_validate({**VALID_COMMUNICATION_DEVICE, "commission_date": "not-a-date"})
