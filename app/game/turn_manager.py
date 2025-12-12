"""
턴 관리자 (Turn Manager)

게임의 턴 순서, 턴 단계, 카드 드로우 등을 관리합니다.
"""

from typing import Optional, Dict, List
from app.models.game import Game
from app.models.player import Player
from app.game.card_manager import CardManager
from app.utils.constants import TurnState, GameState


class TurnManager:
    """
    턴 관리자 클래스
    
    게임의 턴 순서와 단계를 관리합니다.
    """
    
    def __init__(self, game: Game, card_manager: CardManager):
        """
        턴 관리자 초기화
        
        Args:
            game: Game 인스턴스
            card_manager: CardManager 인스턴스
        """
        self.game = game
        self.card_manager = card_manager
    
    def start_turn(self, player_id: str) -> bool:
        """
        플레이어의 턴을 시작합니다.
        
        Args:
            player_id: 턴을 시작할 플레이어 ID
            
        Returns:
            시작 성공 여부
        """
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        if self.game.state != GameState.IN_PROGRESS:
            return False
        
        # 현재 플레이어 설정
        self.game.set_current_player(player_id)
        self.game.set_turn_state(TurnState.DRAW)
        
        # 카드 드로우 단계로 이동
        return self.process_draw_phase(player_id)
    
    def process_draw_phase(self, player_id: str) -> bool:
        """
        카드 드로우 단계를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            처리 성공 여부
        """
        if self.game.current_player_id != player_id:
            return False
        
        if self.game.turn_state != TurnState.DRAW:
            return False
        
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        # 기본 드로우: 2장
        cards_drawn = self.draw_cards_for_player(player_id, 2)
        
        if cards_drawn:
            self.game.add_event(f"{player.name}이(가) 카드 {len(cards_drawn)}장을 뽑았습니다.", "action")
        
        # 카드 사용 단계로 이동
        self.game.set_turn_state(TurnState.PLAY_CARD)
        return True
    
    def draw_cards_for_player(self, player_id: str, count: int) -> List:
        """
        플레이어에게 카드를 드로우합니다.
        
        Args:
            player_id: 플레이어 ID
            count: 드로우할 카드 수
            
        Returns:
            드로우한 카드 목록
        """
        player = self.game.get_player(player_id)
        if not player:
            return []
        
        cards_drawn = []
        
        for _ in range(count):
            # 덱이 비어있으면 재생성
            if self.card_manager.get_deck_count() == 0:
                self.card_manager.reshuffle_discard_pile()
                # 재생성 후에도 비어있으면 종료
                if self.card_manager.get_deck_count() == 0:
                    break
            
            card = self.card_manager.draw_card()
            if card:
                player.add_card(card)
                cards_drawn.append(card)
        
        return cards_drawn
    
    def can_end_turn(self, player_id: str) -> bool:
        """
        플레이어가 턴을 종료할 수 있는지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            턴 종료 가능 여부
        """
        if self.game.current_player_id != player_id:
            return False
        
        if self.game.turn_state not in [TurnState.PLAY_CARD, TurnState.RESPOND]:
            return False
        
        return True
    
    def end_turn(self, player_id: str) -> bool:
        """
        플레이어의 턴을 종료합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            종료 성공 여부
        """
        if not self.can_end_turn(player_id):
            return False
        
        player = self.game.get_player(player_id)
        if not player:
            return False
        
        # 핸드 카드 수 제한 체크 (재력보다 많으면 버려야 함)
        max_hand_size = player.hp
        if player.get_hand_count() > max_hand_size:
            # TODO: 초과 카드 버리기 로직 (향후 구현)
            pass
        
        # 턴 종료 상태로 변경
        self.game.set_turn_state(TurnState.END_TURN)
        self.game.add_event(f"{player.name}의 턴이 종료되었습니다.", "notification")
        
        # 다음 플레이어로 이동
        return self.move_to_next_player()
    
    def move_to_next_player(self) -> bool:
        """
        다음 플레이어로 턴을 이동합니다.
        
        Returns:
            이동 성공 여부
        """
        if not self.game.current_player_id:
            return False
        
        # 다음 플레이어 찾기
        next_player = self.game.get_next_player(self.game.current_player_id)
        
        if not next_player:
            return False
        
        # 턴 번호 증가
        self.game.turn_number += 1
        
        # 다음 플레이어의 턴 시작
        return self.start_turn(next_player.id)
    
    def get_current_player(self) -> Optional[Player]:
        """
        현재 턴 플레이어를 반환합니다.
        
        Returns:
            현재 플레이어 (없으면 None)
        """
        if not self.game.current_player_id:
            return None
        return self.game.get_player(self.game.current_player_id)
    
    def get_next_player(self) -> Optional[Player]:
        """
        다음 턴 플레이어를 반환합니다 (턴을 이동하지 않음).
        
        Returns:
            다음 플레이어 (없으면 None)
        """
        if not self.game.current_player_id:
            return None
        return self.game.get_next_player(self.game.current_player_id)
    
    def is_player_turn(self, player_id: str) -> bool:
        """
        플레이어의 턴인지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            플레이어의 턴 여부
        """
        return self.game.current_player_id == player_id
    
    def can_play_card(self, player_id: str) -> bool:
        """
        플레이어가 카드를 사용할 수 있는지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            카드 사용 가능 여부
        """
        if not self.is_player_turn(player_id):
            return False
        
        if self.game.turn_state != TurnState.PLAY_CARD:
            return False
        
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        return True
    
    def set_respond_phase(self, player_id: str) -> bool:
        """
        대응 단계로 설정합니다 (공격 받을 때).
        
        Args:
            player_id: 대응할 플레이어 ID
            
        Returns:
            설정 성공 여부
        """
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        self.game.set_turn_state(TurnState.RESPOND)
        return True
    
    def return_to_play_phase(self) -> bool:
        """
        카드 사용 단계로 돌아갑니다 (대응 후).
        
        Returns:
            설정 성공 여부
        """
        if not self.game.current_player_id:
            return False
        
        self.game.set_turn_state(TurnState.PLAY_CARD)
        return True
    
    def get_turn_info(self) -> Dict:
        """
        현재 턴 정보를 반환합니다.
        
        Returns:
            턴 정보 딕셔너리
        """
        current_player = self.get_current_player()
        next_player = self.get_next_player()
        
        return {
            "turn_number": self.game.turn_number,
            "current_player_id": self.game.current_player_id,
            "current_player_name": current_player.name if current_player else None,
            "next_player_id": next_player.id if next_player else None,
            "next_player_name": next_player.name if next_player else None,
            "turn_state": self.game.turn_state.value,
        }

