import datetime as dt

import httpx
import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.client import (
    EnergyDataFlowGrouping,
    EnergyDataFlowType,
    GivenergyAPIClient,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

ACCOUNT_PAYLOAD = {
    "id": 2,
    "name": "frank28.203",
    "first_name": "Anna",
    "surname": "Adams",
    "role": "OWNER",
    "email": "kelly44@allen.co.uk",
    "address": "Flat 60\nKyle Lights",
    "postcode": "SP1 1NE",
    "country": "UNITED_KINGDOM",
    "telephone_number": "0738 286 7656",
    "timezone": "GMT",
    "standard_timezone": "Europe/London",
}

COMMUNICATION_DEVICE_PAYLOAD = {
    "serial_number": "WF2345G123",
    "type": "WIFI",
    "firmware_version": 123,
    "commission_date": "2021-01-01T00:00:00Z",
    "inverter": {
        "serial": "CE2345G123",
        "status": "WAITING",
        "last_online": "2023-01-01T00:00:00Z",
        "last_updated": "2023-01-01T00:00:00Z",
        "commission_date": "2021-01-01T00:00:00Z",
        "info": {
            "battery_type": "LITHIUM",
            "battery": {"nominal_capacity": 110, "nominal_voltage": 51.2, "depth_of_discharge": 1},
            "model": "GIV-AC-3.0",
            "max_charge_rate": 2560,
        },
        "warranty": {"type": "Standard", "expiry_date": "2033-01-01T00:00:00Z"},
        "firmware_version": {"ARM": 420, "DSP": 426},
        "connections": {
            "batteries": [
                {
                    "module_number": 1,
                    "serial": "BB2345G123",
                    "firmware_version": 1035,
                    "capacity": {"full": 110, "design": 110},
                    "cell_count": 16,
                    "has_usb": True,
                    "nominal_voltage": 51.2,
                }
            ],
            "meters": [
                {
                    "address": 1,
                    "serial_number": 212345678,
                    "manufacturer_code": "0000",
                    "type_code": 1500,
                    "hardware_version": 1000,
                    "software_version": 1000,
                    "baud_rate": 9600,
                }
            ],
        },
        "flags": [],
    },
}


# ---------------------------------------------------------------------------
# get_account
# ---------------------------------------------------------------------------


class TestGetAccount:

    def test_returns_correct_fields(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            json={"data": ACCOUNT_PAYLOAD},
        )
        account = GivenergyAPIClient(api_key="some-key").get_account()
        assert account.id == 2
        assert account.name == "frank28.203"
        assert account.first_name == "Anna"
        assert account.surname == "Adams"
        assert account.role == "OWNER"
        assert account.email == "kelly44@allen.co.uk"
        assert account.address == "Flat 60\nKyle Lights"
        assert account.postcode == "SP1 1NE"
        assert account.country == "UNITED_KINGDOM"
        assert account.telephone_number == "0738 286 7656"
        assert account.timezone == "GMT"
        assert account.standard_timezone == "Europe/London"

    def test_sends_authorization_header(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            json={"data": ACCOUNT_PAYLOAD},
        )
        GivenergyAPIClient(api_key="my-secret-key").get_account()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["Authorization"] == "Bearer my-secret-key"
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Accept"] == "application/json"

    def test_http_401_raises(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            status_code=401,
        )
        with pytest.raises(Exception):
            GivenergyAPIClient(api_key="bad-key").get_account()

    def test_http_500_raises(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            status_code=500,
        )
        with pytest.raises(Exception):
            GivenergyAPIClient(api_key="some-key").get_account()

    def test_malformed_response_missing_data_key_raises(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            json={"not_data": {}},
        )
        with pytest.raises(KeyError):
            GivenergyAPIClient(api_key="some-key").get_account()

    def test_malformed_response_invalid_email_raises(self, httpx_mock: HTTPXMock) -> None:
        bad_payload = {**ACCOUNT_PAYLOAD, "email": "not-an-email"}
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            json={"data": bad_payload},
        )
        with pytest.raises(Exception):
            GivenergyAPIClient(api_key="some-key").get_account()


# ---------------------------------------------------------------------------
# get_communication_devices (list)
# ---------------------------------------------------------------------------


class TestGetCommunicationDevices:

    def test_returns_list_of_devices(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": [COMMUNICATION_DEVICE_PAYLOAD]},
        )
        devices = GivenergyAPIClient(api_key="some-key").get_communication_devices()
        assert len(devices) == 1

    def test_returns_correct_device_fields(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": [COMMUNICATION_DEVICE_PAYLOAD]},
        )
        devices = GivenergyAPIClient(api_key="some-key").get_communication_devices()
        device = devices[0]
        assert device.serial_number == "WF2345G123"
        assert device.type == "WIFI"
        assert device.firmware_version == 123
        assert device.commission_date == dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc)

    def test_returns_correct_inverter_fields(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": [COMMUNICATION_DEVICE_PAYLOAD]},
        )
        inverter = GivenergyAPIClient(api_key="some-key").get_communication_devices()[0].inverter
        assert inverter.serial == "CE2345G123"
        assert inverter.status.value == "WAITING"
        assert inverter.firmware_version.ARM == 420
        assert inverter.firmware_version.DSP == 426
        assert inverter.warranty.expiry_date == dt.datetime(2033, 1, 1, tzinfo=dt.timezone.utc)
        assert inverter.info.model == "GIV-AC-3.0"
        assert inverter.info.max_charge_rate == 2560

    def test_returns_correct_battery_connection(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": [COMMUNICATION_DEVICE_PAYLOAD]},
        )
        battery = GivenergyAPIClient(api_key="some-key").get_communication_devices()[0].inverter.connections.batteries[0]
        assert battery.serial == "BB2345G123"
        assert battery.module_number == 1
        assert battery.cell_count == 16
        assert battery.has_usb is True
        assert battery.capacity.full == 110
        assert battery.capacity.design == 110

    def test_returns_correct_meter_connection(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": [COMMUNICATION_DEVICE_PAYLOAD]},
        )
        meter = GivenergyAPIClient(api_key="some-key").get_communication_devices()[0].inverter.connections.meters[0]
        assert meter.address == 1
        assert meter.serial_number == 212345678
        assert meter.manufacturer_code == "0000"
        assert meter.baud_rate == 9600

    def test_returns_empty_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": []},
        )
        devices = GivenergyAPIClient(api_key="some-key").get_communication_devices()
        assert devices == []

    def test_sends_authorization_header(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={"data": []},
        )
        GivenergyAPIClient(api_key="my-secret-key").get_communication_devices()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["Authorization"] == "Bearer my-secret-key"

    def test_http_404_raises(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            status_code=404,
        )
        with pytest.raises(Exception):
            GivenergyAPIClient(api_key="some-key").get_communication_devices()


# ---------------------------------------------------------------------------
# get_communication_device (singular)
# ---------------------------------------------------------------------------


class TestGetCommunicationDevice:

    def test_returns_device_by_serial(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device/WF2345G123",
            method="GET",
            json={"data": COMMUNICATION_DEVICE_PAYLOAD},
        )
        device = GivenergyAPIClient(api_key="some-key").get_communication_device(serial_number="WF2345G123")
        assert device.serial_number == "WF2345G123"
        assert device.type == "WIFI"
        assert device.inverter.serial == "CE2345G123"

    def test_serial_number_used_in_url(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device/MY-SERIAL-999",
            method="GET",
            json={"data": {**COMMUNICATION_DEVICE_PAYLOAD, "serial_number": "MY-SERIAL-999"}},
        )
        device = GivenergyAPIClient(api_key="some-key").get_communication_device(serial_number="MY-SERIAL-999")
        request = httpx_mock.get_request()
        assert request is not None
        assert "MY-SERIAL-999" in str(request.url)
        assert device.serial_number == "MY-SERIAL-999"

    def test_sends_authorization_header(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device/WF2345G123",
            method="GET",
            json={"data": COMMUNICATION_DEVICE_PAYLOAD},
        )
        GivenergyAPIClient(api_key="my-secret-key").get_communication_device(serial_number="WF2345G123")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["Authorization"] == "Bearer my-secret-key"

    def test_http_404_raises(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device/UNKNOWN",
            method="GET",
            status_code=404,
        )
        with pytest.raises(Exception):
            GivenergyAPIClient(api_key="some-key").get_communication_device(serial_number="UNKNOWN")


# ---------------------------------------------------------------------------
# get_client context manager
# ---------------------------------------------------------------------------


class TestGetClient:

    def test_yields_client_with_correct_headers(self) -> None:
        api_client = GivenergyAPIClient(api_key="test-key-123")
        with api_client.get_client() as client:
            assert client.headers["Authorization"] == "Bearer test-key-123"
            assert client.headers["Content-Type"] == "application/json"
            assert client.headers["Accept"] == "application/json"

    def test_client_is_closed_after_context_exits(self) -> None:
        api_client = GivenergyAPIClient(api_key="test-key")
        with api_client.get_client() as client:
            assert not client.is_closed
        assert client.is_closed


# ---------------------------------------------------------------------------
# client property
# ---------------------------------------------------------------------------


class TestClientProperty:

    def test_returns_client_with_correct_headers(self) -> None:
        api_client = GivenergyAPIClient(api_key="prop-key")
        client = api_client.client
        assert client.headers["Authorization"] == "Bearer prop-key"
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["Accept"] == "application/json"
        client.close()

    def test_each_access_returns_new_client(self) -> None:
        api_client = GivenergyAPIClient(api_key="prop-key")
        c1 = api_client.client
        c2 = api_client.client
        assert c1 is not c2
        c1.close()
        c2.close()


# ---------------------------------------------------------------------------
# aget_client async context manager
# ---------------------------------------------------------------------------


class TestAgetClient:

    @pytest.mark.asyncio
    async def test_yields_async_client_with_correct_headers(self) -> None:
        api_client = GivenergyAPIClient(api_key="async-key")
        async with api_client.aget_client() as client:
            assert client.headers["Authorization"] == "Bearer async-key"
            assert client.headers["Content-Type"] == "application/json"
            assert client.headers["Accept"] == "application/json"

    @pytest.mark.asyncio
    async def test_async_client_is_closed_after_context_exits(self) -> None:
        api_client = GivenergyAPIClient(api_key="async-key")
        async with api_client.aget_client() as client:
            assert not client.is_closed
        assert client.is_closed


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnergyDataFlowGrouping:

    def test_values(self) -> None:
        assert EnergyDataFlowGrouping.HALF_HOURLY == 0
        assert EnergyDataFlowGrouping.DAILY == 1
        assert EnergyDataFlowGrouping.MONTHLY == 2
        assert EnergyDataFlowGrouping.YEARLY == 3
        assert EnergyDataFlowGrouping.TOTAL == 4

    def test_all_members_present(self) -> None:
        members = {e.name for e in EnergyDataFlowGrouping}
        assert members == {"HALF_HOURLY", "DAILY", "MONTHLY", "YEARLY", "TOTAL"}


class TestEnergyDataFlowType:

    def test_values(self) -> None:
        assert EnergyDataFlowType.PV_TO_HOME == 0
        assert EnergyDataFlowType.PV_TO_BATTERY == 1
        assert EnergyDataFlowType.PV_TO_GRID == 2
        assert EnergyDataFlowType.GRID_TO_HOME == 3
        assert EnergyDataFlowType.GRID_TO_BATTERY == 4
        assert EnergyDataFlowType.BATTERY_TO_HOME == 5
        assert EnergyDataFlowType.BATTERY_TO_GRID == 6

    def test_all_members_present(self) -> None:
        members = {e.name for e in EnergyDataFlowType}
        assert members == {
            "PV_TO_HOME",
            "PV_TO_BATTERY",
            "PV_TO_GRID",
            "GRID_TO_HOME",
            "GRID_TO_BATTERY",
            "BATTERY_TO_HOME",
            "BATTERY_TO_GRID",
        }
