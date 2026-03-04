from pydantic import BaseModel


class PatientCreate(BaseModel):
    name: str
    phone: str
    language_preference: str = "english"


class PatientResponse(BaseModel):
    id: str
    name: str
    language_preference: str
    is_optout: bool
