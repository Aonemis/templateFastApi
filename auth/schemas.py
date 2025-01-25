from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def check_username(cls, value):
        if len(value) < 5 or len(value) > 12:
            raise ValueError("username have less than 5 or more 12 character")
        return value