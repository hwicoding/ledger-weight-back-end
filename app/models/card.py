"""
카드 (Card) 모델
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.utils.constants import CardType, Suit, Rank


class Card(BaseModel):
    """
    카드 모델
    
    게임에서 사용되는 모든 카드를 나타냅니다.
    """
    
    id: str = Field(..., description="카드 고유 ID")
    card_type: CardType = Field(..., description="카드 타입")
    name: str = Field(..., description="카드 이름")
    suit: Optional[Suit] = Field(None, description="카드 무늬 (일부 카드는 무늬 없음)")
    rank: Optional[Rank] = Field(None, description="카드 숫자 (일부 카드는 숫자 없음)")
    range: int = Field(1, description="영향력 (사거리), 기본값 1")
    description: str = Field("", description="카드 설명")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            CardType: lambda v: v.value,
            Suit: lambda v: v.value if v else None,
            Rank: lambda v: v.value if v else None,
        }
    
    def is_bang(self) -> bool:
        """정산 카드 여부"""
        return self.card_type == CardType.BANG
    
    def is_missed(self) -> bool:
        """회피 카드 여부"""
        return self.card_type == CardType.MISSED
    
    def is_beer(self) -> bool:
        """비상금 카드 여부"""
        return self.card_type == CardType.BEER
    
    def is_weapon(self) -> bool:
        """무기 카드 여부"""
        return self.card_type in [CardType.VOLCANIC, CardType.WINCHESTER]
    
    def is_equipment(self) -> bool:
        """장착 카드 여부"""
        return self.card_type in [
            CardType.SCOPE,
            CardType.BARREL,
            CardType.MUSTANG,
            CardType.JAIL,
        ]
    
    def can_target(self, target_range: int) -> bool:
        """
        대상 공격 가능 여부 확인
        
        Args:
            target_range: 대상까지의 거리
            
        Returns:
            공격 가능 여부
        """
        return self.range >= target_range
    
    def __str__(self) -> str:
        suit_str = f" {self.suit.value}" if self.suit else ""
        rank_str = f" {self.rank.value}" if self.rank else ""
        return f"{self.name}{suit_str}{rank_str}"
    
    def __repr__(self) -> str:
        return f"Card(id={self.id}, type={self.card_type.value}, name={self.name})"
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "card_type": self.card_type.value,
            "name": self.name,
            "suit": self.suit.value if self.suit else None,
            "rank": self.rank.value if self.rank else None,
            "range": self.range,
            "description": self.description,
        }

