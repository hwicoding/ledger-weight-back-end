"""
플레이어 (Player) 모델
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.models.role import Role
from app.models.card import Card
from app.utils.constants import Role as RoleEnum, INITIAL_HP, DEFAULT_RANGE


class Player(BaseModel):
    """
    플레이어 모델
    
    게임에 참여하는 플레이어의 상태를 관리합니다.
    """
    
    id: str = Field(..., description="플레이어 고유 ID")
    name: str = Field(..., description="플레이어 이름")
    role: Role = Field(..., description="플레이어 역할")
    hp: int = Field(..., description="재력 (생명력)")
    max_hp: int = Field(..., description="최대 재력")
    range: int = Field(DEFAULT_RANGE, description="기본 영향력 (사거리)")
    hand: List[Card] = Field(default_factory=list, description="핸드 카드 목록")
    equipment: Dict[str, Card] = Field(default_factory=dict, description="장착 카드 (무기, 장착)")
    treasure: Optional[str] = Field(None, description="장착 보물 이름")
    is_alive: bool = Field(True, description="생존 여부")
    position: int = Field(..., description="플레이어 위치 (순서)")
    
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def create(
        cls,
        player_id: str,
        name: str,
        role: RoleEnum,
        position: int,
    ) -> "Player":
        """
        플레이어 생성 팩토리 메서드
        
        Args:
            player_id: 플레이어 ID
            name: 플레이어 이름
            role: 역할 Enum
            position: 플레이어 위치
            
        Returns:
            생성된 Player 인스턴스
        """
        role_obj = Role(role)
        initial_hp = INITIAL_HP[role]
        
        return cls(
            id=player_id,
            name=name,
            role=role_obj,
            hp=initial_hp,
            max_hp=initial_hp,
            range=DEFAULT_RANGE,
            position=position,
            is_alive=True,
        )
    
    def take_damage(self, damage: int = 1) -> bool:
        """
        피해를 받습니다.
        
        Args:
            damage: 받을 피해량 (기본값 1)
            
        Returns:
            사망 여부 (True: 사망, False: 생존)
        """
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.is_alive = False
            return True
        return False
    
    def heal(self, amount: int = 1) -> None:
        """
        재력을 회복합니다.
        
        Args:
            amount: 회복량 (기본값 1)
        """
        self.hp = min(self.max_hp, self.hp + amount)
        if self.hp > 0:
            self.is_alive = True
    
    def add_card(self, card: Card) -> None:
        """핸드에 카드를 추가합니다."""
        self.hand.append(card)
    
    def remove_card(self, card_id: str) -> Optional[Card]:
        """
        핸드에서 카드를 제거합니다.
        
        Args:
            card_id: 제거할 카드 ID
            
        Returns:
            제거된 카드 (없으면 None)
        """
        for i, card in enumerate(self.hand):
            if card.id == card_id:
                return self.hand.pop(i)
        return None
    
    def get_card(self, card_id: str) -> Optional[Card]:
        """
        핸드에서 카드를 조회합니다.
        
        Args:
            card_id: 카드 ID
            
        Returns:
            카드 (없으면 None)
        """
        for card in self.hand:
            if card.id == card_id:
                return card
        return None
    
    def equip_card(self, slot: str, card: Card) -> Optional[Card]:
        """
        장착 카드를 장착합니다.
        
        Args:
            slot: 장착 슬롯 ("weapon", "scope", "barrel", "mustang", "jail")
            card: 장착할 카드
            
        Returns:
            기존에 장착된 카드 (없으면 None)
        """
        old_card = self.equipment.get(slot)
        self.equipment[slot] = card
        return old_card
    
    def get_effective_range(self) -> int:
        """
        현재 유효 영향력 (사거리)을 계산합니다.
        
        Returns:
            유효 영향력
        """
        effective_range = self.range
        
        # 무기 카드의 영향력 적용
        weapon = self.equipment.get("weapon")
        if weapon:
            effective_range = weapon.range
        
        # 첩보원 카드의 영향력 +1
        if "scope" in self.equipment:
            effective_range += 1
        
        return effective_range
    
    def get_hand_count(self) -> int:
        """핸드 카드 개수를 반환합니다."""
        return len(self.hand)
    
    def to_dict(self, hide_hand: bool = False) -> dict:
        """
        딕셔너리로 변환 (WebSocket 전송용)
        
        Args:
            hide_hand: 핸드 카드 숨김 여부 (다른 플레이어 조회 시)
            
        Returns:
            플레이어 정보 딕셔너리
        """
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.name if not hide_hand else None,  # 역할은 자신만 볼 수 있음
            "hp": self.hp,
            "max_hp": self.max_hp,
            "range": self.get_effective_range(),
            "hand_count": self.get_hand_count(),
            "hand": [card.to_dict() for card in self.hand] if not hide_hand else None,
            "equipment": {
                slot: card.to_dict() for slot, card in self.equipment.items()
            },
            "treasure": self.treasure,
            "is_alive": self.is_alive,
            "position": self.position,
        }
    
    def __str__(self) -> str:
        return f"Player({self.name}, {self.role.name}, HP: {self.hp}/{self.max_hp})"
    
    def __repr__(self) -> str:
        return f"Player(id={self.id}, name={self.name}, role={self.role.name})"

