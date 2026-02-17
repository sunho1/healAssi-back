from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn):
    # simple dev-only login
    if data.email == "test" and data.password == "test":
        return {"access_token": "dev-token-123", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
