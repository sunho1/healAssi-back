"""
유저 관련 CRUD 함수
데이터베이스 조회/생성/수정 작업을 수행
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.schemas.user import UserSignupRequest
from app.core.security import SecurityUtils
from datetime import datetime
from typing import Optional


class CRUDUser:
    """유저 관련 CRUD 작업을 수행하는 클래스"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserSignupRequest) -> User:
        """
        새로운 유저 생성
        
        Args:
            db: 데이터베이스 세션
            user_data: 회원가입 요청 데이터
            
        Returns:
            생성된 User 객체
        """
        # 비밀번호를 해시하여 저장
        password_hash = SecurityUtils.hash_password(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        이메일로 유저 조회
        
        Args:
            db: 데이터베이스 세션
            email: 이메일 주소
            
        Returns:
            User 객체 또는 None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        ID로 유저 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 유저 ID
            
        Returns:
            User 객체 또는 None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        사용자 이름으로 유저 조회
        
        Args:
            db: 데이터베이스 세션
            username: 사용자 이름
            
        Returns:
            User 객체 또는 None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def check_email_exists(db: Session, email: str) -> bool:
        """
        이메일이 존재하는지 확인
        
        Args:
            db: 데이터베이스 세션
            email: 이메일 주소
            
        Returns:
            True if 존재, False if 미존재
        """
        return db.query(User).filter(User.email == email).first() is not None
    
    @staticmethod
    def verify_user_password(db: Session, email: str, password: str) -> Optional[User]:
        """
        유저의 비밀번호 검증
        
        Args:
            db: 데이터베이스 세션
            email: 이메일 주소
            password: 평문 비밀번호
            
        Returns:
            인증 성공 시 User 객체, 실패 시 None
        """
        user = CRUDUser.get_user_by_email(db, email)
        
        if user and SecurityUtils.verify_password(password, user.password_hash):
            return user
        
        return None
    
    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """
        유저의 마지막 로그인 시간 업데이트
        
        Args:
            db: 데이터베이스 세션
            user_id: 유저 ID
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
        """
        유저의 비밀번호 변경
        
        Args:
            db: 데이터베이스 세션
            user_id: 유저 ID
            new_password: 새로운 비밀번호 (평문)
            
        Returns:
            업데이트된 User 객체 또는 None
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            user.password_hash = SecurityUtils.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user
        
        return None
    
    @staticmethod
    def find_users_by_username_and_email(
        db: Session, username: str, email: str
    ) -> list[User]:
        """
        사용자 이름과 이메일로 유저 검색
        (아이디 찾기 기능용)
        
        Args:
            db: 데이터베이스 세션
            username: 사용자 이름
            email: 이메일 (전체 또는 부분)
            
        Returns:
            일치하는 User 객체 리스트
        """
        query = db.query(User)
        
        if username:
            query = query.filter(User.username == username)
        
        if email:
            # 이메일 부분 검색
            query = query.filter(User.email.contains(email))
        
        return query.all()
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """
        유저 계정 비활성화
        
        Args:
            db: 데이터베이스 세션
            user_id: 유저 ID
            
        Returns:
            업데이트된 User 객체 또는 None
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user
        
        return None
