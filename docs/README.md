# 장부의 무게 프로젝트 문서

이 디렉토리는 프로젝트의 모든 기술 문서를 포함합니다.

## 문서 구조

```
docs/
├── README.md (이 파일)
├── PROJECT_OVERVIEW.md          # 프로젝트 개요 및 핵심 개념
├── DEVELOPMENT_PLAN.md          # 개발 계획서
├── architecture/                # 아키텍처 설계
│   ├── system-design.md        # 시스템 아키텍처
│   └── api-design.md           # API 설계 원칙
├── database/                    # 데이터베이스 설계
│   ├── schema.md               # 스키마 설계
│   ├── erd.md                  # ERD 다이어그램
│   └── migrations.md           # 마이그레이션 이력
├── fastapi/                     # FastAPI 구현 문서
│   ├── features/               # 기능별 문서
│   │   ├── project-structure.md # 프로젝트 구조 설계
│   │   ├── websocket.md        # WebSocket 구현
│   │   └── ...                 # 각 기능별 문서
│   └── best-practices.md       # FastAPI 베스트 프랙티스 적용
└── deployment/                  # 배포 관련
    └── deployment.md            # 배포 가이드
```

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

