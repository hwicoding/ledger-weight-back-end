# 장부의 무게 프로젝트 문서

이 디렉토리는 프로젝트의 모든 기술 문서를 포함합니다.

## 문서 구조

### 현재 생성된 문서

```
docs/
├── README.md                    # 이 파일 (문서 가이드)
├── PROJECT_OVERVIEW.md          # 프로젝트 개요 및 핵심 개념
├── DEVELOPMENT_PLAN.md          # 6주 개발 계획서
├── architecture/                # 아키텍처 설계
│   └── system-design.md        # ✅ 시스템 아키텍처 (의사결정, 트러블슈팅, 성능 고려사항 포함)
├── database/                    # 데이터베이스 설계 (준비 중)
│   └── (스키마 설계 문서 예정)
├── fastapi/                     # FastAPI 구현 문서
│   ├── best-practices.md       # ✅ FastAPI 베스트 프랙티스 적용
│   └── features/               # 기능별 문서
│       ├── project-structure.md # ✅ 프로젝트 구조 설계 (코드 예시, 의사결정 기록 포함)
│       ├── models.md            # ✅ 모델 클래스 구현 (Role, Card, Player, Game)
│       ├── card-manager.md      # ✅ 카드 관리자 구현 (덱 생성, 셔플, 드로우)
│       ├── game-manager.md      # ✅ 게임 매니저 구현 (게임 생성, 초기화, 승리 조건)
│       ├── turn-manager.md      # ✅ 턴 관리자 구현 (턴 순서, 턴 단계, 카드 드로우)
│       └── action-handler.md    # ✅ 액션 핸들러 구현 (카드 사용, 공격/방어 처리)
└── deployment/                  # 배포 관련 (준비 중)
    └── (배포 가이드 예정)
```

**참고**: 프로젝트 루트의 `logs/` 폴더에는 날짜별 작업일지가 저장됩니다.
- 구조: `logs/YYYY/MM/DD.md`
- 예시: `logs/2025/12/11.md` - 2025년 12월 11일 작업일지

### 문서 상태

| 문서 | 상태 | 설명 |
|------|------|------|
| PROJECT_OVERVIEW.md | ✅ 완료 | 프로젝트 개요, 용어 변환, 역할 및 승리 조건 |
| DEVELOPMENT_PLAN.md | ✅ 완료 | 6주 개발 계획, Phase별 작업 목록 |
| architecture/system-design.md | ✅ 완료 | 시스템 아키텍처, 의사결정, 트러블슈팅, 성능 고려사항 |
| fastapi/best-practices.md | ✅ 완료 | FastAPI 베스트 프랙티스 적용 사항 |
| fastapi/features/project-structure.md | ✅ 완료 | 프로젝트 구조 설계, 코드 예시, 의사결정 기록 |
| fastapi/features/models.md | ✅ 완료 | 모델 클래스 구현 문서 |
| fastapi/features/card-manager.md | ✅ 완료 | 카드 관리자 구현 문서 |
| fastapi/features/game-manager.md | ✅ 완료 | 게임 매니저 구현 문서 |
| fastapi/features/turn-manager.md | ✅ 완료 | 턴 관리자 구현 문서 |
| fastapi/features/action-handler.md | ✅ 완료 | 액션 핸들러 구현 문서 |
| architecture/api-design.md | ⏳ 예정 | API 설계 원칙 |
| database/schema.md | ⏳ 예정 | 데이터베이스 스키마 설계 |
| fastapi/features/websocket.md | ✅ 완료 | WebSocket 구현 |
| deployment/deployment.md | ⏳ 예정 | 배포 가이드 |
| FRONTEND_COORDINATION_PLAN.md | ✅ 완료 | 프론트엔드 연동 작업 계획 |
| NAS_SERVER_SETUP_GUIDE.md | ✅ 완료 | NAS 서버 구축 가이드 |
| DATABASE_RECOMMENDATION.md | ✅ 완료 | 데이터베이스 선택 가이드 |
| DEPLOYMENT_CHECKLIST_RESPONSE.md | ✅ 완료 | 배포 전 확인 사항 답변 |

## 문서 작성 가이드

각 문서에는 다음 내용을 포함합니다:

### 필수 항목
- **코드 예시**: 실제 구현 코드 스니펫
- **의사결정 기록**: 왜 이 방식을 선택했는지
- **트러블슈팅**: 문제와 해결 과정
- **성능 고려사항**: 최적화 포인트

### 문서 작성 원칙
1. 구현 전: 설계 문서 작성
2. 구현 중: 코드와 함께 문서 업데이트
3. 구현 후: 최종 정리 및 개선점 기록

