"""
액션 핸들러 (Action Handler)

플레이어의 액션(카드 사용, 공격 대응 등)을 처리합니다.
"""

from typing import Optional, Dict, List
from app.models.game import Game
from app.models.player import Player
from app.models.card import Card
from app.game.turn_manager import TurnManager
from app.game.card_manager import CardManager
from app.utils.constants import (
    ActionType,
    CardType,
    TurnState,
    GameState,
)


class ActionHandler:
    """
    액션 핸들러 클래스
    
    플레이어의 액션을 처리하고 게임 상태를 업데이트합니다.
    """
    
    def __init__(
        self,
        game: Game,
        turn_manager: TurnManager,
        card_manager: CardManager,
    ):
        """
        액션 핸들러 초기화
        
        Args:
            game: Game 인스턴스
            turn_manager: TurnManager 인스턴스
            card_manager: CardManager 인스턴스
        """
        self.game = game
        self.turn_manager = turn_manager
        self.card_manager = card_manager
    
    def handle_action(
        self,
        action_type: ActionType,
        player_id: str,
        data: Dict,
    ) -> Dict:
        """
        플레이어 액션을 처리합니다.
        
        Args:
            action_type: 액션 타입
            player_id: 플레이어 ID
            data: 액션 데이터
            
        Returns:
            처리 결과 딕셔너리
            {
                "success": bool,
                "message": str,
                "event": str
            }
        """
        if self.game.state != GameState.IN_PROGRESS:
            return {
                "success": False,
                "message": "게임이 진행 중이 아닙니다.",
                "event": None,
            }
        
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return {
                "success": False,
                "message": "플레이어를 찾을 수 없거나 사망했습니다.",
                "event": None,
            }
        
        # 액션 타입별 처리
        if action_type == ActionType.USE_CARD:
            return self.handle_use_card(player_id, data)
        elif action_type == ActionType.RESPOND_ATTACK:
            return self.handle_respond_attack(player_id, data)
        elif action_type == ActionType.END_TURN:
            return self.handle_end_turn(player_id)
        else:
            return {
                "success": False,
                "message": f"지원하지 않는 액션 타입: {action_type}",
                "event": None,
            }
    
    def handle_use_card(self, player_id: str, data: Dict) -> Dict:
        """
        카드 사용 액션을 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            data: {
                "card_id": str,
                "target_id": Optional[str]  # 대상 플레이어 ID (공격 카드 등)
            }
            
        Returns:
            처리 결과
        """
        if not self.turn_manager.can_play_card(player_id):
            return {
                "success": False,
                "message": "카드를 사용할 수 없는 상태입니다.",
                "event": None,
            }
        
        player = self.game.get_player(player_id)
        card_id = data.get("card_id")
        target_id = data.get("target_id")
        
        if not card_id:
            return {
                "success": False,
                "message": "카드 ID가 필요합니다.",
                "event": None,
            }
        
        # 카드 조회
        card = player.get_card(card_id)
        if not card:
            return {
                "success": False,
                "message": "카드를 찾을 수 없습니다.",
                "event": None,
            }
        
        # 카드 타입별 처리
        if card.is_bang():
            return self.handle_bang_card(player_id, card, target_id)
        elif card.is_missed():
            return {
                "success": False,
                "message": "회피 카드는 공격 대응 시에만 사용할 수 있습니다.",
                "event": None,
            }
        elif card.is_beer():
            return self.handle_beer_card(player_id, card)
        else:
            return {
                "success": False,
                "message": f"아직 구현되지 않은 카드 타입: {card.card_type.value}",
                "event": None,
            }
    
    def handle_bang_card(
        self,
        player_id: str,
        card: Card,
        target_id: Optional[str],
    ) -> Dict:
        """
        정산 카드 사용을 처리합니다.
        
        Args:
            player_id: 공격하는 플레이어 ID
            card: 정산 카드
            target_id: 대상 플레이어 ID
            
        Returns:
            처리 결과
        """
        if not target_id:
            return {
                "success": False,
                "message": "공격 대상이 필요합니다.",
                "event": None,
            }
        
        attacker = self.game.get_player(player_id)
        target = self.game.get_player(target_id)
        
        if not attacker or not target:
            return {
                "success": False,
                "message": "플레이어를 찾을 수 없습니다.",
                "event": None,
            }
        
        if not target.is_alive:
            return {
                "success": False,
                "message": "대상 플레이어가 이미 사망했습니다.",
                "event": None,
            }
        
        # 자신을 공격할 수 없음
        if attacker.id == target.id:
            return {
                "success": False,
                "message": "자신을 공격할 수 없습니다.",
                "event": None,
            }
        
        # 거리 및 영향력 확인
        distance = self.game.calculate_distance(attacker, target)
        effective_range = attacker.get_effective_range()
        
        if effective_range < distance:
            return {
                "success": False,
                "message": f"거리가 너무 멉니다. (필요: {distance}, 현재: {effective_range})",
                "event": None,
            }
        
        # 카드 제거
        removed_card = attacker.remove_card(card.id)
        if not removed_card:
            return {
                "success": False,
                "message": "카드를 제거할 수 없습니다.",
                "event": None,
            }
        
        # 카드 버리기
        self.card_manager.discard_card(removed_card)
        
        # 공격 처리
        event_message = f"{attacker.name}이(가) {target.name}에게 정산을 시도했습니다."
        self.game.add_event(event_message)
        
        # 대응 단계로 설정
        self.turn_manager.set_respond_phase(target_id)
        
        return {
            "success": True,
            "message": "정산 카드를 사용했습니다. 대상 플레이어가 대응할 수 있습니다.",
            "event": event_message,
        }
    
    def handle_beer_card(self, player_id: str, card: Card) -> Dict:
        """
        비상금 카드 사용을 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            card: 비상금 카드
            
        Returns:
            처리 결과
        """
        player = self.game.get_player(player_id)
        if not player:
            return {
                "success": False,
                "message": "플레이어를 찾을 수 없습니다.",
                "event": None,
            }
        
        # 재력이 최대치인지 확인
        if player.hp >= player.max_hp:
            return {
                "success": False,
                "message": "재력이 이미 최대치입니다.",
                "event": None,
            }
        
        # 카드 제거
        removed_card = player.remove_card(card.id)
        if not removed_card:
            return {
                "success": False,
                "message": "카드를 제거할 수 없습니다.",
                "event": None,
            }
        
        # 카드 버리기
        self.card_manager.discard_card(removed_card)
        
        # 재력 회복
        old_hp = player.hp
        player.heal(1)
        
        event_message = f"{player.name}이(가) 비상금을 사용하여 재력을 {old_hp}에서 {player.hp}로 회복했습니다."
        self.game.add_event(event_message)
        
        return {
            "success": True,
            "message": "비상금을 사용하여 재력을 1 회복했습니다.",
            "event": event_message,
        }
    
    def handle_respond_attack(self, player_id: str, data: Dict) -> Dict:
        """
        공격 대응 액션을 처리합니다.
        
        Args:
            player_id: 대응하는 플레이어 ID
            data: {
                "card_id": str  # 회피 카드 ID
            }
            
        Returns:
            처리 결과
        """
        if self.game.turn_state != TurnState.RESPOND:
            return {
                "success": False,
                "message": "대응할 수 없는 상태입니다.",
                "event": None,
            }
        
        player = self.game.get_player(player_id)
        card_id = data.get("card_id")
        
        if not card_id:
            return {
                "success": False,
                "message": "카드 ID가 필요합니다.",
                "event": None,
            }
        
        # 카드 조회
        card = player.get_card(card_id)
        if not card:
            return {
                "success": False,
                "message": "카드를 찾을 수 없습니다.",
                "event": None,
            }
        
        # 회피 카드인지 확인
        if not card.is_missed():
            return {
                "success": False,
                "message": "회피 카드만 사용할 수 있습니다.",
                "event": None,
            }
        
        # 카드 제거
        removed_card = player.remove_card(card.id)
        if not removed_card:
            return {
                "success": False,
                "message": "카드를 제거할 수 없습니다.",
                "event": None,
            }
        
        # 카드 버리기
        self.card_manager.discard_card(removed_card)
        
        event_message = f"{player.name}이(가) 회피 카드를 사용하여 공격을 막았습니다."
        self.game.add_event(event_message)
        
        # 원래 플레이어의 턴으로 복귀
        if self.game.current_player_id:
            self.turn_manager.return_to_play_phase()
        
        return {
            "success": True,
            "message": "공격을 회피했습니다.",
            "event": event_message,
        }
    
    def handle_respond_attack_failed(self, player_id: str) -> Dict:
        """
        공격 대응 실패 (회피 카드 없음)를 처리합니다.
        
        Args:
            player_id: 대응하는 플레이어 ID
            
        Returns:
            처리 결과
        """
        if self.game.turn_state != TurnState.RESPOND:
            return {
                "success": False,
                "message": "대응할 수 없는 상태입니다.",
                "event": None,
            }
        
        player = self.game.get_player(player_id)
        if not player:
            return {
                "success": False,
                "message": "플레이어를 찾을 수 없습니다.",
                "event": None,
            }
        
        # 피해 받기
        died = player.take_damage(1)
        
        if died:
            event_message = f"{player.name}이(가) 공격을 받아 재력이 0이 되어 사망했습니다."
        else:
            event_message = f"{player.name}이(가) 공격을 받아 재력이 {player.hp}로 감소했습니다."
        
        self.game.add_event(event_message)
        
        # 원래 플레이어의 턴으로 복귀
        if self.game.current_player_id:
            self.turn_manager.return_to_play_phase()
        
        return {
            "success": True,
            "message": "공격을 받았습니다.",
            "event": event_message,
        }
    
    def handle_end_turn(self, player_id: str) -> Dict:
        """
        턴 종료 액션을 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            처리 결과
        """
        if not self.turn_manager.can_end_turn(player_id):
            return {
                "success": False,
                "message": "턴을 종료할 수 없는 상태입니다.",
                "event": None,
            }
        
        success = self.turn_manager.end_turn(player_id)
        
        if success:
            return {
                "success": True,
                "message": "턴이 종료되었습니다.",
                "event": f"{self.game.get_player(player_id).name}의 턴이 종료되었습니다.",
            }
        else:
            return {
                "success": False,
                "message": "턴 종료에 실패했습니다.",
                "event": None,
            }
    
    def validate_action(
        self,
        action_type: ActionType,
        player_id: str,
        data: Dict,
    ) -> tuple[bool, Optional[str]]:
        """
        액션 유효성을 검증합니다.
        
        Args:
            action_type: 액션 타입
            player_id: 플레이어 ID
            data: 액션 데이터
            
        Returns:
            (유효성 여부, 에러 메시지)
        """
        if self.game.state != GameState.IN_PROGRESS:
            return False, "게임이 진행 중이 아닙니다."
        
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False, "플레이어를 찾을 수 없거나 사망했습니다."
        
        if action_type == ActionType.USE_CARD:
            if not self.turn_manager.can_play_card(player_id):
                return False, "카드를 사용할 수 없는 상태입니다."
            
            card_id = data.get("card_id")
            if not card_id:
                return False, "카드 ID가 필요합니다."
            
            card = player.get_card(card_id)
            if not card:
                return False, "카드를 찾을 수 없습니다."
        
        elif action_type == ActionType.RESPOND_ATTACK:
            if self.game.turn_state != TurnState.RESPOND:
                return False, "대응할 수 없는 상태입니다."
            
            card_id = data.get("card_id")
            if not card_id:
                return False, "카드 ID가 필요합니다."
            
            card = player.get_card(card_id)
            if not card:
                return False, "카드를 찾을 수 없습니다."
            
            if not card.is_missed():
                return False, "회피 카드만 사용할 수 있습니다."
        
        elif action_type == ActionType.END_TURN:
            if not self.turn_manager.can_end_turn(player_id):
                return False, "턴을 종료할 수 없는 상태입니다."
        
        return True, None

