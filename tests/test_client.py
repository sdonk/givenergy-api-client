from pytest_httpx import HTTPXMock

from givenergy_api_client.client import GivenergyAPIClient


class TestClient:
    def test_get_account(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/account",
            method="GET",
            json={
                "data": {
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
            },
        )
        assert GivenergyAPIClient(api_key="some-key").get_account()

    def test_get_communication_devices(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device",
            method="GET",
            json={
                "data": [
                    {
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
                                        "firmware_version": "1035",
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
                ]
            },
        )
        assert GivenergyAPIClient(api_key="some-key").get_communication_devices()

    def test_get_communication_device(self, httpx_mock: HTTPXMock) -> None:
        cd_payload = {
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
                "connections": {"batteries": [], "meters": []},
                "flags": [],
            },
        }
        httpx_mock.add_response(
            url="https://api.givenergy.cloud/v1/communication-device/WF2345G123",
            method="GET",
            json={"data": cd_payload},
        )
        result = GivenergyAPIClient(api_key="some-key").get_communication_device(serial_number="WF2345G123")
        assert result.serial_number == "WF2345G123"

    async def test_alist_ev_chargers_async(self, httpx_mock: HTTPXMock) -> None:
        charger = {
            "uuid": "uuid-1234",
            "serial_number": "EV001",
            "type": "AC",
            "alias": "Home Charger",
            "online": False,
            "status": "Unavailable",
        }
        meta = {"current_page": 1, "last_page": 1, "per_page": 15, "total": 1}
        httpx_mock.add_response(method="GET", json={"data": [charger], "meta": meta})
        result = await GivenergyAPIClient(api_key="some-key").alist_ev_chargers()
        assert result.data[0].serial_number == "EV001"
