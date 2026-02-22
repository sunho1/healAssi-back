"""
인증 관련 API 엔드포인트
회원가입, 로그인, 아이디/비밀번호 찾기 등의 기능
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.api.deps import get_db
from app.schemas.user import (
    UserSignupRequest,
    UserLoginRequest,
    LoginResponse,
    TokenResponse,
    UserResponse,
    FindIdRequest,
    FindIdResponse,
    FindPasswordRequest,
    PasswordResetResponse,
    MessageResponse
)
from app.crud.crud_user import CRUDUser
from app.core.security import SecurityUtils
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


# ============ 회원가입 ============

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignupRequest, db: Session = Depends(get_db)):
    """
    회원가입 엔드포인트
    
    - 이메일, 사용자 이름, 비밀번호를 받아 등록
    - 비밀번호는 해시하여 저장
    """
    # 이미 등록된 이메일인지 확인
    if CRUDUser.check_email_exists(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일이 이미 등록되었습니다."
        )
    
    # 새로운 유저 생성
    new_user = CRUDUser.create_user(db, user_data)
    
    return new_user


# ============ 로그인 ============

@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLoginRequest, db: Session = Depends(get_db)):
    """
    로그인 엔드포인트
    
    - 이메일과 비밀번호로 인증
    - 성공하면 JWT 토큰(액세스, 리프레시) 발급
    """
    # 비밀번호 검증
    user = CRUDUser.verify_user_password(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 맞지 않습니다."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다."
        )
    
    # 액세스 토큰 생성
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # 리프레시 토큰 생성
    refresh_token = SecurityUtils.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # 마지막 로그인 시간 업데이트
    CRUDUser.update_last_login(db, user.id)
    
    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ============ 토큰 갱신 ============

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    """
    리프레시 토큰으로 새로운 액세스 토큰 발급
    """
    # 리프레시 토큰 검증
    payload = SecurityUtils.verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다."
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    # 새로운 액세스 토큰 생성
    new_access_token = SecurityUtils.create_access_token(
        data={"sub": user_id, "email": email}
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# ============ 아이디 찾기 ============

@router.post("/find-id", response_model=FindIdResponse)
def find_id(request: FindIdRequest, db: Session = Depends(get_db)):
    """
    아이디(이메일) 찾기 엔드포인트
    
    - 사용자 이름과 이메일로 등록된 이메일 조회
    - 보안을 위해 이메일을 부분적으로 마스킹
    """
    # 사용자 이름과 이메일로 검색
    users = CRUDUser.find_users_by_username_and_email(
        db,
        username=request.username,
        email=request.email
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자를 찾을 수 없습니다."
        )
    
    # 첫 번째 결과 사용
    user = users[0]
    
    # 이메일 마스킹 (예: user@example.com -> us**@example.com)
    email_parts = user.email.split("@")
    local_part = email_parts[0]
    domain_part = email_parts[1]
    
    # 로컬 부분을 부분 마스킹
    masked_local = local_part[:2] + "*" * max(1, len(local_part) - 2)
    masked_email = f"{masked_local}@{domain_part}"
    
    return {
        "email": masked_email,
        "message": "이메일을 찾았습니다."
    }


# ============ 비밀번호 찾기 ============

@router.post("/find-password", response_model=PasswordResetResponse)
def find_password(request: FindPasswordRequest, db: Session = Depends(get_db)):
    """
    비밀번호 찾기 엔드포인트
    
    - 이메일로 등록된 사용자 확인
    - 비밀번호 재설정 토큰 발급 (실제로는 이메일로 발송)
    """
    # 이메일로 유저 조회
    user = CRUDUser.get_user_by_email(db, request.email)
    
    if not user:
        # 보안상 실제로 없어도 메시지는 동일하게
        return {
            "message": "등록된 이메일로 비밀번호 재설정 링크를 전송했습니다."
        }
    
    # 비밀번호 재설정 토큰 생성 (유효기간 1시간)
    reset_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # 실제 운영에서는 여기서 이메일로 토큰을 포함한 링크를 발송합니다.
    # 본 예시에서는 토큰을 응답에 포함시킵니다.
    return {
        "message": "비밀번호 재설정 링크를 이메일로 전송했습니다.",
        "reset_token": reset_token
    }


# ============ 비밀번호 재설정 ============

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    비밀번호 재설정 엔드포인트
    
    - 재설정 토큰으로 검증 후 비밀번호 변경
    """
    # 토큰 검증
    payload = SecurityUtils.verify_token(token)
    
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 재설정 토큰입니다."
        )
    
    user_id = int(payload.get("sub"))
    
    # 비밀번호 업데이트
    updated_user = CRUDUser.update_password(db, user_id, new_password)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return {"message": "비밀번호가 성공적으로 재설정되었습니다."}


# ============ 마이페이지 - 내 정보 조회 (인증 필요) ============

@router.get("/me", response_model=UserResponse)
def get_current_user(current_user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    """
    현재 로그인한 사용자의 정보 조회
    
    - JWT 토큰으로 인증
    """
    user = CRUDUser.get_user_by_id(db, current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return user


def verify_token(token: str) -> int:
    """
    JWT 토큰 검증 및 유저 ID 추출
    
    인증이 필요한 엔드포인트에서 Depends()로 사용
    """
    # 실제로는 Authorization 헤더에서 토큰을 추출해야 합니다.
    # 이 함수는 예시이며, 실제 구현에서는 FastAPI의 권장 방식을 따릅니다.
    
    payload = SecurityUtils.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )
    
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다."
        )
    
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰 형식입니다."
        )

