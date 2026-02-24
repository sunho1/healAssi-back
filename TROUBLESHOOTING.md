# Railway 배포 트러블슈팅 히스토리

> **프로젝트**: HealAssi Backend (FastAPI)
> **배포 플랫폼**: Railway
> **최종 업데이트**: 2026-02-25

---

## 📅 2026-02-25 - Railway 배포 에러 해결

### 🔴 문제 #1: DATABASE_URL 설정 에러

**발생 시간**: 초기 배포 시도

**에러 메시지**:
```
ValidationError: DATABASE_URL field required
```

**원인**:
- `config.py`에서 `DATABASE_URL`이 필수 필드로 정의됨
- 환경변수가 없으면 앱 시작 시 즉시 에러 발생
- Railway의 `postgres://` 프로토콜과 SQLAlchemy의 `postgresql://` 불일치

**해결 방법**:

1. **[app/core/config.py](app/core/config.py) 수정**
   ```python
   # Before
   DATABASE_URL: str  # 필수 필드, 기본값 없음

   # After
   DATABASE_URL: str = "sqlite:///./health.db"  # 기본값 추가

   @property
   def SQLALCHEMY_DATABASE_URL(self) -> str:
       db_url = self.DATABASE_URL
       # Railway의 postgres:// → postgresql:// 자동 변환
       if db_url.startswith("postgres://"):
           db_url = db_url.replace("postgres://", "postgresql://", 1)
       return db_url
   ```

2. **불필요한 import 제거**
   ```python
   # import os 제거 (더 이상 사용하지 않음)
   ```

**결과**: ✅ 데이터베이스 연결 설정 정상화

---

### 🔴 문제 #2: Nixpacks 빌드 실패

**발생 시간**: 첫 배포 시도 후

**에러 메시지**:
```
UndefinedVar: Usage of undefined variable '$NIXPACKS_PATH'
/bin/bash: line 1: pip: command not found
Build Failed: build daemon returned an error
```

**원인**:
- 커스텀 `nixpacks.toml` 설정이 Railway의 자동 감지와 충돌
- pip 명령어를 찾을 수 없음
- Nixpacks 환경변수 참조 오류

**해결 방법**:

1. **nixpacks.toml 삭제**
   ```bash
   rm nixpacks.toml
   ```

2. **[railway.json](railway.json) 단순화**
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"  // 자동 감지 사용
     },
     "deploy": {
       "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "healthCheckPath": "/"
     }
   }
   ```

3. **Railway 자동 감지 활용**
   - `requirements.txt` → 의존성 자동 설치
   - `runtime.txt` → Python 버전 자동 설정

**결과**: ✅ 빌드 성공

---

### 🔴 문제 #3: email-validator 버전 충돌

**발생 시간**: 빌드 성공 후 signup API 호출 시

**에러 메시지**:
```python
AttributeError: 'ValidatedEmail' object has no attribute 'normalized'
```

**원인**:
- Pydantic v2 (2.5.0)는 `email-validator` 2.0+ 필요
- 기존 `email-validator==1.3.1`은 Pydantic v1용
- `EmailStr` 타입 사용 시 호환성 문제 발생

**해결 방법**:

**[requirements.txt](requirements.txt) 수정**
```diff
- email-validator==1.3.1
+ email-validator==2.1.0

- gunicorn==21.2.0  # 제거 (사용하지 않음)
```

**영향받은 스키마**:
- `UserSignupRequest` (회원가입)
- `UserLoginRequest` (로그인)
- `FindIdRequest` (아이디 찾기)
- `FindPasswordRequest` (비밀번호 찾기)

**결과**: ✅ EmailStr 타입 정상 작동

---

### 🔴 문제 #4: bcrypt 비밀번호 길이 제한

**발생 시간**: email-validator 수정 후

**에러 메시지**:
```
ValueError: password cannot be longer than 72 bytes,
truncate manually if necessary (e.g. my_password[:72])
```

**원인**:
- bcrypt는 최대 **72바이트**까지만 해시 가능
- 비밀번호 필드에 `max_length` 제한이 없음
- 긴 비밀번호 입력 시 에러 발생

**해결 방법**:

1. **[app/schemas/user.py](app/schemas/user.py) - 길이 제한 추가**
   ```python
   # UserSignupRequest
   password: str = Field(
       ...,
       min_length=8,
       max_length=72,  # bcrypt 제한
       description="비밀번호 (8-72자, bcrypt 제한)"
   )

   # ResetPasswordRequest
   new_password: str = Field(
       ...,
       min_length=8,
       max_length=72,
       description="새로운 비밀번호 (8-72자, bcrypt 제한)"
   )
   ```

2. **[app/core/security.py](app/core/security.py) - 방어 코드 추가**
   ```python
   @staticmethod
   def hash_password(password: str) -> str:
       """
       비밀번호를 해시하여 저장
       bcrypt는 72바이트 제한이 있으므로,
       필요시 자동으로 잘라냅니다.
       """
       password_bytes = password.encode('utf-8')
       if len(password_bytes) > 72:
           # 72바이트로 자르기
           password = password_bytes[:72].decode('utf-8', errors='ignore')

       return pwd_context.hash(password)
   ```

**결과**: ✅ 회원가입 정상 작동

---

## 🛠️ 추가 개선 사항

### 로깅 및 에러 핸들링 강화

**파일**: [app/main.py](app/main.py)

1. **데이터베이스 초기화 로깅**
   ```python
   try:
       logger.info(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URL[:20]}...")
       Base.metadata.create_all(bind=engine)
       logger.info("Database tables created successfully")
   except Exception as e:
       logger.error(f"Database initialization error: {str(e)}")
       raise
   ```

2. **전역 예외 핸들러**
   ```python
   @app.exception_handler(Exception)
   async def global_exception_handler(request: Request, exc: Exception):
       logger.error(f"Global exception: {str(exc)}", exc_info=True)
       return JSONResponse(
           status_code=500,
           content={"detail": "Internal server error", "error": str(exc)}
       )
   ```

3. **Health Check 개선**
   ```python
   from sqlalchemy import text

   @app.get("/api/health")
   def health_check():
       try:
           db = SessionLocal()
           db.execute(text("SELECT 1"))  # SQLAlchemy 2.x 호환
           db.close()
           return {"status": "healthy", "database": "connected"}
       except Exception as e:
           logger.error(f"Health check failed: {str(e)}", exc_info=True)
           return {"status": "unhealthy", "database": "disconnected"}
   ```

---

### 인증 엔드포인트 로깅

**파일**: [app/api/v1/endpoints/auth.py](app/api/v1/endpoints/auth.py)

```python
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignupRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Signup attempt for email: {user_data.email}")

        if CRUDUser.check_email_exists(db, user_data.email):
            logger.warning(f"Email already exists: {user_data.email}")
            raise HTTPException(...)

        new_user = CRUDUser.create_user(db, user_data)
        logger.info(f"User created successfully: {new_user.id}")

        return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"
        )
```

---

## 📋 최종 변경 파일 목록

| 파일 | 변경 사항 | 이유 |
|------|----------|------|
| `app/core/config.py` | DATABASE_URL 기본값 추가, postgres→postgresql 변환 | Railway 호환성 |
| `app/main.py` | 로깅, 전역 예외 핸들러, health check 개선 | 디버깅 용이성 |
| `app/api/v1/endpoints/auth.py` | signup 로깅 추가 | 에러 추적 |
| `app/schemas/user.py` | password max_length=72 추가 | bcrypt 제한 |
| `app/core/security.py` | 72바이트 초과 시 자동 절단 | 방어 코드 |
| `requirements.txt` | email-validator 1.3.1→2.1.0 | Pydantic v2 호환 |
| `railway.json` | 설정 단순화 | 자동 감지 활용 |
| `nixpacks.toml` | 삭제 | 충돌 제거 |
| `Procfile` | uvicorn 직접 사용 | 단순화 |

---

## ✅ 배포 체크리스트

### Railway 환경변수 설정
- [x] `DATABASE_URL` - PostgreSQL 자동 생성됨
- [x] `SECRET_KEY` - 강력한 키로 변경 필요 (`openssl rand -hex 32`)

### 파일 확인
- [x] `.gitignore`에 `.env`, `*.db` 포함
- [x] `requirements.txt` 의존성 정확
- [x] `runtime.txt` Python 버전 명시 (3.11.7)

### API 테스트
- [x] `GET /` - Welcome 메시지
- [x] `GET /api/health` - 데이터베이스 연결 확인
- [x] `POST /api/v1/auth/signup` - 회원가입
- [x] `POST /api/v1/auth/login` - 로그인

---

## 🔍 디버깅 방법

### Railway 로그 확인

**대시보드:**
1. Railway 프로젝트 페이지
2. Deployments → 최신 배포
3. View Logs

**CLI:**
```bash
railway logs -f  # 실시간 로그
```

### 로컬 테스트

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 로컬 실행
uvicorn app.main:app --reload --port 8000

# 테스트
curl http://localhost:8000/
curl http://localhost:8000/api/health
```

---

## 📚 참고 자료

- [Railway 문서](https://docs.railway.app)
- [FastAPI 문서](https://fastapi.tiangolo.com)
- [Pydantic v2 마이그레이션](https://docs.pydantic.dev/latest/migration/)
- [bcrypt 제한사항](https://pypi.org/project/bcrypt/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)

---

---

### 🔴 문제 #5: passlib과 bcrypt 버전 충돌

**발생 시간**: 문제 #4 수정 후

**에러 메시지**:
```
AttributeError: module 'bcrypt' has no attribute '__about__'
WARNING:passlib.handlers.bcrypt:(trapped) error reading bcrypt version
password cannot be longer than 72 bytes
```

**원인**:
- `passlib[bcrypt]==1.7.4`는 오래된 버전
- bcrypt 버전이 명시되지 않아 최신 4.2.0 설치됨
- bcrypt 4.0+에서 `__about__` 속성 제거로 passlib과 호환 문제
- passlib이 bcrypt 버전을 읽을 수 없어 에러 발생

**해결 방법**:

**[requirements.txt](requirements.txt) - bcrypt 버전 명시**
```diff
  passlib[bcrypt]==1.7.4
+ bcrypt==4.0.1
  python-jose[cryptography]==3.3.0
```

**bcrypt 버전 선택 이유**:
- `bcrypt==4.0.1`: passlib 1.7.4와 호환되는 최신 안정 버전
- `bcrypt==3.2.2`: 더 안전하지만 구버전
- `bcrypt==4.1.0+`: passlib 1.7.4와 호환 문제 있음

**결과**: ✅ bcrypt 정상 작동

---

## 📝 업데이트 로그

| 날짜 | 작성자 | 내용 |
|------|--------|------|
| 2026-02-25 | Claude | Railway 배포 에러 수정 (5건) |
| 2026-02-25 | Claude | 로깅 및 에러 핸들링 강화 |

---

## 📋 최종 의존성 버전

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1              # ← 명시적 버전 지정
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
pytz==2023.3
email-validator==2.1.0     # ← Pydantic v2 호환
```

---

**다음 배포 시 확인 사항:**
1. SECRET_KEY를 프로덕션용으로 변경했는지 확인
2. CORS 설정에 프론트엔드 URL 추가 확인
3. Railway PostgreSQL이 정상 연결되었는지 확인
4. 배포 후 health check 엔드포인트 테스트
