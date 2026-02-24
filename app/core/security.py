"""
보안 관련 유틸리티: 비밀번호 해싱, JWT 토큰 생성/검증
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# 비밀번호 해싱 설정 (bcrypt 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    """보안 관련 유틸리티 클래스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호를 해시하여 저장

        bcrypt는 72바이트 제한이 있으므로,
        필요시 자동으로 잘라냅니다.
        """
        # bcrypt는 72바이트까지만 처리 가능
        # UTF-8 인코딩 시 72바이트를 초과할 수 있으므로 체크
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # 72바이트로 자르기
            password = password_bytes[:72].decode('utf-8', errors='ignore')

        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """입력받은 비밀번호와 해시된 비밀번호가 일치하는지 확인"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        
        # 만료 시간 설정
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        # JWT 토큰 생성
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """리프레시 토큰 생성"""
        to_encode = data.copy()
        
        # 리프레시 토큰의 만료 시간은 더 길게 설정
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """토큰을 검증하고 페이로드 반환"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None
