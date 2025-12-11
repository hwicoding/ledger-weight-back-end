"""
카드 관리자 (Card Manager)

카드 덱 생성, 셔플, 드로우, 버리기 등의 카드 관리 로직을 담당합니다.
"""

import random
from typing import List, Optional
from app.models.card import Card
from app.utils.constants import (
    CardType,
    Suit,
    Rank,
    CARD_DECK_CONFIG,
    CARD_DETAILS,
)


class CardManager:
    """
    카드 관리자 클래스
    
    카드 덱의 생성, 셔플, 드로우, 버리기 등을 관리합니다.
    """
    
    def __init__(self):
        """카드 관리자 초기화"""
        self.deck: List[Card] = []
        self.discard_pile: List[Card] = []
    
    def create_deck(self) -> List[Card]:
        """
        카드 덱을 생성합니다.
        
        Returns:
            생성된 카드 덱
        """
        deck: List[Card] = []
        card_counter = 0
        
        # 각 카드 타입별로 지정된 수만큼 생성
        for card_type, count in CARD_DECK_CONFIG.items():
            card_info = CARD_DETAILS[card_type]
            
            for i in range(count):
                card_id = f"{card_type.value}_{card_counter:03d}"
                
                # 무늬와 숫자가 있는 카드인지 확인
                suit = None
                rank = None
                
                # 정산, 회피, 비상금 카드는 무늬와 숫자가 있음
                if card_type in [CardType.BANG, CardType.MISSED, CardType.BEER]:
                    # 무늬와 숫자 할당 (순환)
                    suits = [Suit.SPADES, Suit.CLUBS, Suit.HEARTS, Suit.DIAMONDS]
                    ranks = [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK]
                    
                    suit_index = (card_counter // len(ranks)) % len(suits)
                    rank_index = card_counter % len(ranks)
                    
                    suit = suits[suit_index]
                    rank = ranks[rank_index]
                
                card = Card(
                    id=card_id,
                    card_type=card_type,
                    name=card_info["name"],
                    suit=suit,
                    rank=rank,
                    range=card_info["range"],
                    description=card_info["description"],
                )
                
                deck.append(card)
                card_counter += 1
        
        self.deck = deck
        return deck
    
    def shuffle(self) -> None:
        """
        덱을 셔플합니다.
        """
        if self.deck:
            random.shuffle(self.deck)
    
    def draw_card(self) -> Optional[Card]:
        """
        덱에서 카드를 한 장 뽑습니다.
        
        Returns:
            뽑은 카드 (덱이 비어있으면 None)
        """
        if not self.deck:
            return None
        
        return self.deck.pop(0)
    
    def draw_cards(self, count: int) -> List[Card]:
        """
        덱에서 카드를 여러 장 뽑습니다.
        
        Args:
            count: 뽑을 카드 수
            
        Returns:
            뽑은 카드 목록
        """
        cards: List[Card] = []
        for _ in range(count):
            card = self.draw_card()
            if card:
                cards.append(card)
            else:
                break  # 덱이 비어있으면 중단
        return cards
    
    def discard_card(self, card: Card) -> None:
        """
        카드를 버림 더미에 추가합니다.
        
        Args:
            card: 버릴 카드
        """
        self.discard_pile.append(card)
    
    def discard_cards(self, cards: List[Card]) -> None:
        """
        여러 카드를 버림 더미에 추가합니다.
        
        Args:
            cards: 버릴 카드 목록
        """
        self.discard_pile.extend(cards)
    
    def get_discard_top(self) -> Optional[Card]:
        """
        버림 더미의 맨 위 카드를 반환합니다 (제거하지 않음).
        
        Returns:
            버림 더미 맨 위 카드 (없으면 None)
        """
        if not self.discard_pile:
            return None
        return self.discard_pile[-1]
    
    def reshuffle_discard_pile(self) -> None:
        """
        버림 더미를 덱으로 재생성합니다.
        
        덱이 비어있을 때 버림 더미를 셔플하여 새로운 덱으로 만듭니다.
        맨 위 카드(마지막에 버려진 카드)는 제외합니다.
        """
        if not self.discard_pile:
            return
        
        # 맨 위 카드 제외
        top_card = self.discard_pile.pop() if self.discard_pile else None
        
        # 나머지 카드를 덱으로 이동
        self.deck = self.discard_pile.copy()
        self.discard_pile.clear()
        
        # 맨 위 카드 다시 추가
        if top_card:
            self.discard_pile.append(top_card)
        
        # 덱 셔플
        self.shuffle()
    
    def get_deck_count(self) -> int:
        """
        덱의 남은 카드 수를 반환합니다.
        
        Returns:
            덱의 카드 수
        """
        return len(self.deck)
    
    def get_discard_count(self) -> int:
        """
        버림 더미의 카드 수를 반환합니다.
        
        Returns:
            버림 더미의 카드 수
        """
        return len(self.discard_pile)
    
    def reset(self) -> None:
        """
        카드 관리자를 초기화합니다.
        """
        self.deck.clear()
        self.discard_pile.clear()
    
    def create_full_deck_and_shuffle(self) -> List[Card]:
        """
        전체 덱을 생성하고 셔플합니다.
        
        Returns:
            생성되고 셔플된 카드 덱
        """
        self.reset()
        deck = self.create_deck()
        self.shuffle()
        return deck

