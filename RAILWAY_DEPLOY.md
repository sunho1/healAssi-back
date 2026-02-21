# Railway 배포 가이드

## 빠른 시작 (3단계)

### 1. GitHub에 코드 푸시
```bash
cd healAssi-back
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 2. Railway에서 배포
1. https://railway.app에 로그인
2. **+ New Project** 클릭
3. **Deploy from GitHub** 선택
4. `healAssi` 저장소 선택
5. `healAssi-back` 디렉토리 선택 (루트 폴더로 자동 감지됨)
6. 자동 배포 시작

### 3. PostgreSQL 데이터베이스 연동
1. Railway 프로젝트에서 **+ New** 클릭
2. **Database** → **PostgreSQL** 선택
3. 자동으로 `DATABASE_URL` 환경변수 생성됨

## 파일 구조

배포를 위해 다음 파일들이 설정되었습니다:

| 파일 | 용도 |
|------|------|
| `Procfile` | gunicorn + uvicorn 실행 명령 |
| `runtime.txt` | Python 3.11.7 버전 지정 |
| `railway.json` | Railway 배포 설정 (선택) |
| `requirements.txt` | Python 의존성 패키지 |
| `.env.example` | 환경변수 템플릿 |

## 환경변수 설정

Railway 대시보드에서 **Variables** 탭에서 다음을 설정하세요:
- `DATABASE_URL`: PostgreSQL 자동 생성 (수동 설정 불필요)

## 배포 후 확인

```bash
# 배포된 앱 상태 확인
curl https://<app-name>.up.railway.app/

# 응답 예상:
# {"message": "Welcome to HealAssi API (Layered Architecture)"}

# 워크아웃 API 테스트
curl https://<app-name>.up.railway.app/api/v1/workouts/
```

## Railway CLI로 배포 (대안)

```bash
# Railway CLI 설치
brew install railway  # macOS

# 로그인
railway login

# 프로젝트 링크
railway link <project-id>

# 배포
railway up
```

## 주의사항

✅ **이렇게 하세요:**
- `.gitignore`에 `health.db`, `.env` 포함되어 있는지 확인
- 프로덕션은 PostgreSQL 사용 (SQLite는 부적합)
- 환경변수는 Railway 대시보드에서 관리

❌ **이렇게 하지 마세요:**
- `.env` 파일을 GitHub에 커밋
- `health.db` SQLite 파일을 커밋
- 로컬 개발용 설정을 프로덕션에 직접 사용

## CORS 설정

웹 앱을 배포한 후 해당 URL을 `app/core/config.py`에 추가:

```python
BACKEND_CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-frontend-app.vercel.app",  # 웹 앱 URL
]
```

## 문제 해결

**"ModuleNotFoundError" 에러**
- `requirements.txt`에 모든 패키지가 명시되어 있는지 확인

**데이터베이스 연결 실패**
- PostgreSQL 데이터베이스가 Railway에 추가되었는지 확인
- `DATABASE_URL` 환경변수가 제대로 설정되었는지 확인

**배포 로그 보기**
```bash
railway logs -f  # Railway CLI 사용
```

## 배포 후 웹과 연동

앞서 생성한 `src/services/api.ts`의 기본 URL은 `http://localhost:8000`입니다.
프로덕션 배포 후 `.env` 또는 환경변수로 설정하세요:

```bash
# healAssi-web/.env
VITE_API_URL=https://<your-railway-app>.up.railway.app/api/v1
```

완료되면 웹 앱에서 백엔드 API를 호출할 수 있습니다! 🚀
