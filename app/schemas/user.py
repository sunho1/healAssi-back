"""
유저 관련 Pydantic 스키마
요청/응답 데이터 검증 및 문서화용
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ============ 회원가입 관련 스키마 ============

class UserSignupRequest(BaseModel):
    """회원가입 요청"""
    email: EmailStr = Field(..., description="이메일 주소")
    username: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "securepassword123"
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "securepassword123"
            }
        }
    }


# ============ 로그인 관련 스키마 ============

class UserLoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class TokenResponse(BaseModel):
    """JWT 토큰 응답"""
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class LoginResponse(BaseModel):
    """로그인 응답"""
    user: 'UserResponse'
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ============ 아이디 찾기 관련 스키마 ============

class FindIdRequest(BaseModel):
    """아이디 찾기 요청"""
    username: str = Field(..., description="사용자 이름")
    email: EmailStr = Field(..., description="이메일 주소")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "user@example.com"
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "user@example.com"
            }
        }
    }


class FindIdResponse(BaseModel):
    """아이디 찾기 응답"""
    email: str = Field(..., description="찾은 이메일 (일부 마스킹)")
    message: str = Field(..., description="결과 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "us**@example.com",
                "message": "이메일을 찾았습니다."
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "us**@example.com",
                "message": "이메일을 찾았습니다."
            }
        }
    }


# ============ 비밀번호 찾기 관련 스키마 ============

class FindPasswordRequest(BaseModel):
    """비밀번호 찾기 요청"""
    email: EmailStr = Field(..., description="이메일 주소")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com"
            }
        }
    }


class ResetPasswordRequest(BaseModel):
    """비밀번호 재설정 요청"""
    token: str = Field(..., description="비밀번호 재설정 토큰")
    new_password: str = Field(..., min_length=8, description="새로운 비밀번호 (최소 8자)")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset-token-xyz...",
                "new_password": "newpassword123"
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "reset-token-xyz...",
                "new_password": "newpassword123"
            }
        }
    }


class PasswordResetResponse(BaseModel):
    """비밀번호 재설정 응답"""
    message: str = Field(..., description="결과 메시지")
    reset_token: Optional[str] = Field(None, description="비밀번호 재설정 토큰")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "비밀번호 재설정 링크를 이메일로 전송했습니다.",
                "reset_token": "reset-token-xyz..."
            }
        }
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "비밀번호 재설정 링크를 이메일로 전송했습니다.",
                "reset_token": "reset-token-xyz..."
            }
        }
    }


# ============ 유저 응답 관련 스키마 ============

class UserResponse(BaseModel):
    """유저 정보 응답"""
    id: int = Field(..., description="유저 ID")
    email: str = Field(..., description="이메일")
    username: str = Field(..., description="사용자 이름")
    is_active: bool = Field(..., description="활성화 여부")
    is_verified: bool = Field(..., description="이메일 인증 여부")
    created_at: datetime = Field(..., description="가입일")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-15T10:30:00",
                "last_login": None
            }
        }
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-15T10:30:00",
                "last_login": None
            }
        }
    }


class UserDetailResponse(UserResponse):
    """유저 상세 정보 응답"""
    pass


class MessageResponse(BaseModel):
    """일반 메시지 응답"""
    message: str = Field(..., description="메시지")
