# 문서 인덱스

빠른 문서 탐색을 위한 인덱스입니다.

## 📚 시작하기

1. **[프로젝트 개요](PROJECT_OVERVIEW.md)** - 프로젝트 소개 및 핵심 개념
2. **[개발 계획서](DEVELOPMENT_PLAN.md)** - 6주 개발 로드맵

## 🏗️ 아키텍처

- **[시스템 아키텍처](architecture/system-design.md)** - 전체 시스템 설계, 의사결정 기록, 성능 고려사항

## 💻 FastAPI 구현

### 기본
- **[베스트 프랙티스](fastapi/best-practices.md)** - 적용된 FastAPI 베스트 프랙티스

### 기능별 문서
- **[프로젝트 구조](fastapi/features/project-structure.md)** - 폴더 구조 설계 및 의사결정
- **[모델 클래스](fastapi/features/models.md)** - Role, Card, Player, Game 모델 구현
- **[카드 관리자](fastapi/features/card-manager.md)** - 카드 덱 생성, 셔플, 드로우 로직
- **[게임 매니저](fastapi/features/game-manager.md)** - 게임 생성, 초기화, 승리 조건 체크
- **[턴 관리자](fastapi/features/turn-manager.md)** - 턴 순서, 턴 단계, 카드 드로우 관리
- **[액션 핸들러](fastapi/features/action-handler.md)** - 카드 사용, 공격/방어 처리

## 📝 문서 작성 가이드

각 문서는 다음 항목을 포함합니다:
- ✅ 코드 예시
- ✅ 의사결정 기록
- ✅ 트러블슈팅
- ✅ 성능 고려사항

## 📦 배포 및 운영

- **[프론트엔드 연동 계획](FRONTEND_COORDINATION_PLAN.md)** - 프론트엔드 연동 작업 계획
- **[NAS 서버 구축 가이드](NAS_SERVER_SETUP_GUIDE.md)** - 서버 환경 구축 가이드
- **[데이터베이스 추천](DATABASE_RECOMMENDATION.md)** - DB 선택 가이드
- **[배포 전 확인 사항](DEPLOYMENT_CHECKLIST_RESPONSE.md)** - 배포 준비 체크리스트

## 📋 작업일지

프로젝트 루트의 `logs/` 폴더에 날짜별 작업일지가 저장됩니다.
- 구조: `logs/YYYY/MM/DD.md`
- 예시: `logs/2025/12/11.md` - 2025년 12월 11일 작업일지
- 각 작업일지에는 작업 시간, 완료한 작업, 이슈 및 해결, 다음 작업 계획 등이 포함됩니다.

## 🔄 문서 업데이트 이력

- 2025-12-11: 프로젝트 기본 구조 및 모델 클래스 문서화 완료
- 2025-12-11: 카드 관리자 및 게임 매니저 문서화 완료
- 2025-12-11: 턴 관리자 문서화 완료
- 2025-12-11: 액션 핸들러 문서화 완료
- 2025-12-11: WebSocket 구현 문서화 완료
- 2025-12-11: 프론트엔드 연동 및 배포 가이드 작성 완료

