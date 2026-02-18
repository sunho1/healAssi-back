# Railway 배포 가이드

## 준비 사항
- Railway 계정 (https://railway.app)
- GitHub 저장소 연동 (권장)

## 배포 단계

### 1. 로컬 테스트
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 로컬 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Railway에 배포

#### GitHub 연동 (쉬운 방법)
1. GitHub에 코드 푸시
2. Railway 대시보드에서 "New Project"
3. "Deploy from GitHub" 선택
4. healAssi 저장소 선택
5. 자동 배포 시작

#### CLI 배포
```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 생성 및 배포
railway init
railway up
```

### 3. 환경변수 설정
Railway 대시보드에서:
- **Variables** → **Add variable**
- 필요한 환경변수 추가 (DATABASE_URL은 PostgreSQL 자동 연동 시 자동 설정됨)

```
DATABASE_URL=postgresql://user:password@host/dbname
```

### 4. PostgreSQL 데이터베이스 연동
1. Railway 프로젝트에서 **+ New Service**
2. **Database** → **PostgreSQL** 선택
3. 자동으로 `DATABASE_URL` 환경변수 생성됨

### 5. CORS 설정 확인
웹 앱 배포 URL을 config.py의 BACKEND_CORS_ORIGINS에 추가:

```python
BACKEND_CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-frontend-domain.vercel.app",  # 웹 앱 URL
]
```

## 주의사항
- `.env` 파일은 로컬에서만 사용하고, 커밋하지 않기
- Railway는 PostgreSQL을 권장 (SQLite는 프로덕션에 부적합)
- `health.db` SQLite 파일을 `.gitignore`에 추가

## 배포 후 확인
```bash
# Railway 로그 보기
railway logs

# 배포된 앱 상태 확인
https://your-app-name.up.railway.app/
# 응답: {"message": "Welcome to HealAssi API (Layered Architecture)"}
```

## 문제 해결
- 로그에서 에러 메시지 확인
- 환경변수가 제대로 설정되었는지 확인
- PostgreSQL 연결 문제 시 DATABASE_URL 형식 확인
