"""
게임 상수 정의
"""

from enum import Enum
from typing import Dict, List

# ==================== 역할 (Role) ====================
class Role(str, Enum):
    """플레이어 역할"""
    SHERIFF = "상단주"  # Sheriff
    DEPUTY = "원로원"  # Deputy
    OUTLAW = "적도 세력"  # Outlaw
    RENEGADE = "야망가"  # Renegade


# ==================== 카드 무늬 (Suit) ====================
class Suit(str, Enum):
    """카드 무늬"""
    SPADES = "검"  # ♠
    CLUBS = "책"  # ♣
    HEARTS = "치유"  # ♥
    DIAMONDS = "돈"  # ♦


# ==================== 카드 숫자 (Rank) ====================
class Rank(str, Enum):
    """카드 숫자"""
    ACE = "상"  # A
    KING = "대"  # K
    QUEEN = "중"  # Q
    JACK = "소"  # J


# ==================== 카드 타입 ====================
class CardType(str, Enum):
    """카드 타입"""
    # 공격 카드
    BANG = "정산"  # Bang!
    MISSED = "회피"  # Missed!
    GATLING = "전원 견제"  # Gatling
    INDIANS = "패거리 습격"  # Indians
    DUEL = "승부"  # Duel
    
    # 회복 카드
    BEER = "비상금"  # Beer
    
    # 무기 카드
    VOLCANIC = "연속 상환 요구"  # Volcanic
    WINCHESTER = "독점 상권 선언"  # Winchester
    
    # 장착 카드
    SCOPE = "첩보원"  # Scope
    BARREL = "신의 한 수"  # Barrel
    MUSTANG = "세력권 경계"  # Mustang
    JAIL = "영업 금지"  # Jail
    
    # 특수 카드
    PANIC = "강제 압류"  # Panic!
    SALOON = "공개 연회"  # Saloon
    GENERAL_STORE = "자선 경매"  # General Store


# ==================== 게임 상태 ====================
class GameState(str, Enum):
    """게임 상태"""
    WAITING = "대기 중"  # 플레이어 대기
    STARTING = "시작 중"  # 게임 시작 준비
    IN_PROGRESS = "진행 중"  # 게임 진행 중
    FINISHED = "종료"  # 게임 종료


class TurnState(str, Enum):
    """턴 상태"""
    DRAW = "드로우"  # 카드 뽑기 단계
    PLAY_CARD = "카드 사용"  # 카드 사용 단계
    RESPOND = "대응"  # 공격 대응 단계
    END_TURN = "턴 종료"  # 턴 종료


# ==================== 액션 타입 ====================
class ActionType(str, Enum):
    """플레이어 액션 타입"""
    USE_CARD = "USE_CARD"  # 카드 사용
    RESPOND_ATTACK = "RESPOND_ATTACK"  # 공격 대응
    END_TURN = "END_TURN"  # 턴 종료
    DRAW_CARD = "DRAW_CARD"  # 카드 뽑기


# ==================== 보물 (Treasure) ====================
# 보물 이름 상수
TREASURE_NAMES = {
    "거대 금고": "Willy the Kid",  # 턴당 정산 무제한
    "협상 증표": "Calamity Janet",  # 정산 ↔ 회피 상호 전환
    "비밀 장부": "Sid Ketchum",  # 카드 2장으로 재력 1 회복
    "비전서": "Black Jack",  # 드로우 시 첫 카드가 치유/돈이면 추가 드로우
    "비밀 창고": "Jourdonnais",  # 공격 시 카드 뽑기 성공 시 피해 무효화
    # TODO: 나머지 11개 보물 추가
}

# ==================== 게임 규칙 상수 ====================
INITIAL_HP = {
    Role.SHERIFF: 5,  # 상단주: 재력 5
    Role.DEPUTY: 4,  # 원로원: 재력 4
    Role.OUTLAW: 3,  # 적도 세력: 재력 3
    Role.RENEGADE: 4,  # 야망가: 재력 4
}

DEFAULT_RANGE = 1  # 기본 영향력 (사거리)

# ==================== 카드 덱 구성 ====================
# TODO: 실제 카드 구성 추가 필요
CARD_DECK_CONFIG: Dict[str, int] = {
    # 예시 (실제 구성은 게임 규칙에 맞게 수정 필요)
    CardType.BANG: 25,
    CardType.MISSED: 12,
    CardType.BEER: 6,
    # ... 나머지 카드들
}

