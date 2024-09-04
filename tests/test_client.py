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
