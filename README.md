# ledger-weight-back-end

장부의 무게 - WebSocket 기반 실시간 카드 게임 백엔드 서버

## 📋 프로젝트 개요

- **프로젝트명**: 장부의 무게 (Ledger Weight)
- **기술 스택**: FastAPI + Python 3.8+
- **통신 방식**: WebSocket 기반 실시간 통신
- **원작**: BANG! 카드 게임

## 🚀 빠른 시작

### 환경 설정

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 열어서 필요한 설정 수정
   ```

3. **서버 실행**
   ```bash
   # 개발 모드
   uvicorn app.main:app --reload
   
   # 프로덕션 모드
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

### 주요 엔드포인트

- `GET /` - 서버 정보
- `GET /health` - 헬스 체크
- `GET /docs` - API 문서 (Swagger UI)
- `GET /redoc` - API 문서 (ReDoc)
- `WS /ws/{player_id}` - WebSocket 연결

## 📚 문서

자세한 문서는 [docs/](docs/) 디렉토리를 참고하세요.

- [프로젝트 개요](docs/PROJECT_OVERVIEW.md)
- [개발 계획서](docs/DEVELOPMENT_PLAN.md)
- [NAS 서버 구축 가이드](docs/NAS_SERVER_SETUP_GUIDE.md)

## 🛠️ 개발 환경

- Python 3.8+
- FastAPI 0.104.1
- Uvicorn 0.24.0

## 📝 라이선스

이 프로젝트는 포트폴리오 목적으로 개발되었습니다.
