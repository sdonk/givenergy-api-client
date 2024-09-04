from pydantic import BaseModel, ConfigDict, EmailStr


class Account(BaseModel):
    id: int
    name: str
    first_name: str
    surname: str
    role: str
    email: EmailStr
    address: str
    postcode: str
    country: str
    telephone_number: str
    timezone: str
    standard_timezone: str

    model_config = ConfigDict(frozen=True)
