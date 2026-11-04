from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class ValidateRequest(BaseModel):
    token: str


class LogoutRequest(BaseModel):
    token: str


class LogoutResponse(BaseModel):
    success: bool
