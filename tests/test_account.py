import pytest
from pydantic import ValidationError

from givenergy_api_client.account import Account

VALID_ACCOUNT_DATA = {
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


class TestAccountModel:

    def test_valid_construction(self) -> None:
        account = Account.model_validate(VALID_ACCOUNT_DATA)
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

    def test_is_immutable(self) -> None:
        account = Account.model_validate(VALID_ACCOUNT_DATA)
        with pytest.raises(ValidationError):
            account.first_name = "Changed"  # type: ignore[misc]

    def test_invalid_email_raises(self) -> None:
        bad_data = {**VALID_ACCOUNT_DATA, "email": "not-an-email"}
        with pytest.raises(ValidationError):
            Account.model_validate(bad_data)

    def test_missing_required_field_raises(self) -> None:
        for field in VALID_ACCOUNT_DATA:
            incomplete = {k: v for k, v in VALID_ACCOUNT_DATA.items() if k != field}
            with pytest.raises(ValidationError):
                Account.model_validate(incomplete)

    def test_id_must_be_int(self) -> None:
        bad_data = {**VALID_ACCOUNT_DATA, "id": "not-an-int"}
        with pytest.raises(ValidationError):
            Account.model_validate(bad_data)

    def test_email_domain_is_normalised_to_lowercase(self) -> None:
        data = {**VALID_ACCOUNT_DATA, "email": "User@Example.COM"}
        account = Account.model_validate(data)
        # Pydantic normalises the domain to lowercase but preserves the local part
        assert account.email == "User@example.com"
