# HealAssi Backend - Railway 배포 가이드

## 🚀 빠른 배포 (3단계)

### 1단계: Railway 프로젝트 생성

1. [Railway](https://railway.app)에 로그인
2. **New Project** 클릭
3. **Deploy from GitHub repo** 선택
4. `healAssi-back` 저장소/폴더 선택

### 2단계: PostgreSQL 데이터베이스 추가

1. Railway 프로젝트 대시보드에서 **+ New** 클릭
2. **Database** → **Add PostgreSQL** 선택
3. Railway가 자동으로 `DATABASE_URL` 환경변수를 생성합니다

### 3단계: 환경변수 설정 (선택사항)

Railway 대시보드 → **Variables** 탭에서:

```env
SECRET_KEY=your-production-secret-key-here
DATABASE_URL=<자동 생성됨>
```

**중요**: `SECRET_KEY`는 다음 명령으로 생성하세요:
```bash
openssl rand -hex 32
```

## ✅ 배포 확인

배포가 완료되면 Railway가 제공하는 URL로 접속:

```bash
# 루트 엔드포인트 확인
curl https://your-app.up.railway.app/

# 응답 예시:
{
  "message": "Welcome to HealAssi API (Layered Architecture)",
  "version": "1.0.0",
  "status": "running"
}

# 헬스 체크
curl https://your-app.up.railway.app/api/health

# API 문서 확인
https://your-app.up.railway.app/docs
```

## 🔧 주요 수정 사항 (이미 적용됨)

### 1. Database URL 처리
Railway는 `postgres://`를 제공하지만 SQLAlchemy는 `postgresql://`이 필요합니다.
[config.py](app/core/config.py#L12-L17)에서 자동 변환 처리:

```python
@property
def SQLALCHEMY_DATABASE_URL(self) -> str:
    db_url = self.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url
```

### 2. 환경변수 기본값
[config.py](app/core/config.py#L9)에서 DATABASE_URL에 기본값 설정:
```python
DATABASE_URL: str = "sqlite:///./health.db"  # 로컬 개발용
```

### 3. 로깅 및 에러 핸들링
[main.py](app/main.py)에 다음 기능 추가:
- 애플리케이션 시작 시 로깅
- 전역 예외 핸들러
- 데이터베이스 연결 테스트가 포함된 헬스 체크

### 4. Railway 배포 설정
- [railway.json](railway.json): Railway 배포 설정
- [Procfile](Procfile): Heroku 호환성 (선택사항)
- [runtime.txt](runtime.txt): Python 3.11.7 사용

## 📝 환경변수 목록

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `DATABASE_URL` | ✅ | `sqlite:///./health.db` | Railway PostgreSQL이 자동 생성 |
| `SECRET_KEY` | ⚠️ | 개발용 키 | **반드시 프로덕션 키로 변경** |
| `PROJECT_NAME` | ❌ | `HealAssi API` | API 프로젝트 이름 |
| `API_V1_STR` | ❌ | `/api/v1` | API 버전 경로 |

## 🌐 CORS 설정

프론트엔드를 배포한 후 [config.py](app/core/config.py#L20-L25)에 URL 추가:

```python
BACKEND_CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://healassi-web.vercel.app",
    "https://heal-assistant.vercel.app",
    "https://your-new-frontend.vercel.app",  # 새 프론트엔드 URL 추가
]
```

변경 후 Git에 커밋하고 푸시하면 Railway가 자동으로 재배포합니다.

## 🐛 문제 해결

### 1. "Application failed to respond" 에러
**원인**: 데이터베이스 연결 실패

**해결**:
```bash
# Railway CLI로 로그 확인
railway logs

# 데이터베이스가 추가되었는지 확인
# Railway 대시보드 → Services → PostgreSQL 확인
```

### 2. "Database connection error"
**원인**: `DATABASE_URL` 환경변수 누락 또는 잘못된 형식

**해결**:
- Railway 대시보드 → Variables에서 `DATABASE_URL` 확인
- PostgreSQL 서비스와 앱이 같은 프로젝트에 있는지 확인

### 3. "ModuleNotFoundError"
**원인**: 의존성 패키지 누락

**해결**:
```bash
# requirements.txt 확인
cat requirements.txt

# 로컬에서 테스트
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. CORS 에러
**원인**: 프론트엔드 URL이 허용 목록에 없음

**해결**:
[config.py](app/core/config.py#L20)의 `BACKEND_CORS_ORIGINS`에 프론트엔드 URL 추가

## 📊 Railway CLI 사용 (선택사항)

```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
railway link

# 실시간 로그 보기
railway logs -f

# 로컬에서 Railway 환경변수로 실행
railway run uvicorn app.main:app --reload
```

## 🔐 보안 체크리스트

- [ ] `SECRET_KEY`를 강력한 값으로 변경
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] PostgreSQL 사용 (SQLite는 프로덕션 부적합)
- [ ] CORS 설정에 실제 프론트엔드 URL만 포함
- [ ] 민감한 정보가 코드에 하드코딩되지 않았는지 확인

## 📈 모니터링

Railway 대시보드에서:
- **Metrics**: CPU, 메모리, 네트워크 사용량
- **Logs**: 실시간 애플리케이션 로그
- **Deployments**: 배포 히스토리 및 롤백

## 🔄 업데이트 배포

```bash
# 코드 변경 후
git add .
git commit -m "Update feature"
git push origin main

# Railway가 자동으로 재배포합니다
```

## 📞 지원

문제가 계속되면:
1. [Railway 문서](https://docs.railway.app) 참고
2. Railway Discord 커뮤니티 문의
3. 프로젝트 이슈 트래커에 보고
