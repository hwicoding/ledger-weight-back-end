"""
액션 핸들러 (Action Handler)

플레이어의 액션(카드 사용, 공격 대응 등)을 처리합니다.
"""

import random
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
    Suit,
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
    
    def _perform_judgement(self, player: Player, success_suits: List[Suit]) -> bool:
        """
        판정용 카드 뽑기 로직.
        
        - 기본: 카드 1장을 뽑아 버림 더미에 놓고, 무늬가 success_suits 중 하나면 성공.
        - 만능 통보(럭키 듀크): 카드 2장을 보고 유리한 쪽 선택.
          - 성공 카드가 있으면 그 카드를 판정 카드로, 나머지는 덱 맨 아래로 보냅니다.
          - 없으면 첫 번째 카드를 판정 카드로, 나머지는 덱 맨 아래로 보냅니다.
        """
        def _ensure_deck() -> None:
            if self.card_manager.get_deck_count() == 0:
                self.card_manager.reshuffle_discard_pile()
        
        treasure = getattr(player, "treasure", None)
        has_lucky = treasure == "만능 통보"
        
        if has_lucky:
            _ensure_deck()
            first = self.card_manager.draw_card()
            _ensure_deck()
            second = self.card_manager.draw_card()
            cards = [c for c in [first, second] if c is not None]
            if not cards:
                return False
            
            # 성공 카드 우선 선택
            success_card = next(
                (c for c in cards if c.suit in success_suits),
                None,
            )
            if success_card:
                chosen = success_card
                other_cards = [c for c in cards if c is not success_card]
                success = True
            else:
                chosen = cards[0]
                other_cards = cards[1:]
                success = False
            
            # 판정 카드는 버림 더미로
            self.card_manager.discard_card(chosen)
            # 나머지는 덱 맨 아래로
            for other in other_cards:
                self.card_manager.put_card_to_bottom(other)
            return success
        
        # 기본 판정: 카드 1장
        _ensure_deck()
        card = self.card_manager.draw_card()
        if not card:
            return False
        self.card_manager.discard_card(card)
        return card.suit in success_suits
    
    def _trigger_suzy_if_needed(self, player: Player) -> None:
        """
        화수분 (수지 라파예트):
        내 손패가 0장이 되는 즉시 덱에서 카드 2장을 드로우.
        """
        if getattr(player, "treasure", None) != "화수분":
            return
        if player.get_hand_count() != 0:
            return
        
        cards = self.turn_manager.draw_cards_for_player(player.id, 2)
        if cards:
            self.game.add_event(
                f"{player.name}의 화수분 효과로 카드 {len(cards)}장을 드로우했습니다.",
                "action",
            )
    
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
        elif action_type == ActionType.USE_TREASURE:
            return self.handle_use_treasure(player_id, data)
        elif action_type == ActionType.SELECT_STEAL_CARD:
            return self.handle_select_steal_card(player_id, data)
        elif action_type == ActionType.SELECT_DRAW_ORDER:
            return self.handle_select_draw_order(player_id, data)
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
        
        # 보물: 반전 금화(칼라미티 제인) – 정산 ↔ 회피 교차 사용
        player_treasure = getattr(player, "treasure", None)
        has_calamity_treasure = player_treasure == "반전 금화"
        
        # 카드 타입별 처리
        if card.is_bang():
            # 정산 기본: 공격으로 사용
            return self.handle_bang_card(player_id, card, target_id)
        elif card.is_missed():
            # 회피 카드는 기본적으로 공격 단계에서 사용 불가
            # 단, 반전 금화 보유 시에는 정산처럼 사용할 수 있음
            if has_calamity_treasure:
                return self.handle_bang_card(player_id, card, target_id)
            return {
                "success": False,
                "message": "회피 카드는 공격 대응 시에만 사용할 수 있습니다.",
                "event": None,
            }
        elif card.is_beer():
            return self.handle_beer_card(player_id, card)
        elif card.card_type == CardType.PANIC:
            return self.handle_panic_card(player_id, card, target_id)
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
        
        # 정산 사용 횟수 및 황금 연갑 (윌리 더 키드) 처리
        attacker_treasure = getattr(attacker, "treasure", None)
        has_willy = attacker_treasure == "황금 연갑"
        bang_count = self.game.turn_attack_counters.get(attacker.id, 0)
        
        # 기본 규칙: 턴당 1회
        if not has_willy and bang_count >= 1:
            return {
                "success": False,
                "message": "이 턴에는 더 이상 정산 카드를 사용할 수 없습니다.",
                "event": None,
            }
        
        # 황금 연갑: 두 번째 정산부터는 추가로 카드 1장 버려야 함
        if has_willy and bang_count >= 1:
            other_cards = [c for c in attacker.hand if c.id != card.id]
            if not other_cards:
                return {
                    "success": False,
                    "message": "황금 연갑 효과로 추가로 버릴 카드가 없어 정산을 사용할 수 없습니다.",
                    "event": None,
                }
            extra_card = random.choice(other_cards)
            removed_extra = attacker.remove_card(extra_card.id)
            if removed_extra:
                self.card_manager.discard_card(removed_extra)
                self.game.add_event(
                    f"{attacker.name}이(가) 황금 연갑 효과로 카드를 1장 추가로 버렸습니다.",
                    "action",
                )
        
        # 낙인 인장 (슬래브 더 키러):
        # 나의 정산 방어에 회피 2장 필요 (내 손패가 상대보다 많을 때만 발동)
        required_missed = 1
        if getattr(attacker, "treasure", None) == "낙인 인장":
            if attacker.get_hand_count() > target.get_hand_count():
                required_missed = 2
        
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
        
        # 화수분 (수지 라파예트): 손패가 0장이 되면 2장 드로우
        self._trigger_suzy_if_needed(attacker)
        
        # 정산 사용 횟수 카운트 업데이트
        self.game.turn_attack_counters[attacker.id] = bang_count + 1
        
        # 공격 처리
        event_message = f"{attacker.name}이(가) {target.name}에게 정산을 시도했습니다."
        self.game.add_event(event_message, "action")
        
        # 대응 단계로 설정 (낙인 인장 효과에 따른 회피 장수 적용)
        self.turn_manager.set_respond_phase(target_id, required_missed=required_missed)
        
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
        
        # 화수분 (수지 라파예트): 손패가 0장이 되면 2장 드로우
        self._trigger_suzy_if_needed(player)
        
        # 재력 회복
        old_hp = player.hp
        player.heal(1)
        
        event_message = f"{player.name}이(가) 비상금을 사용하여 재력을 {old_hp}에서 {player.hp}로 회복했습니다."
        self.game.add_event(event_message, "action")
        
        return {
            "success": True,
            "message": "비상금을 사용하여 재력을 1 회복했습니다.",
            "event": event_message,
        }

    def handle_panic_card(self, player_id: str, card: Card, target_id: Optional[str]) -> Dict:
        """
        강제 압류 (PANIC) 카드 사용을 처리합니다.
        - 사거리 1 내의 플레이어 카드 1장을 강탈합니다.
        - 천청 방울 보유 시: 상대 손패 2장을 무작위로 확인 후 1장을 선택하여 가져옵니다.
        """
        if not target_id:
            return {
                "success": False,
                "message": "강탈 대상이 필요합니다.",
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
        if attacker.id == target.id:
            return {
                "success": False,
                "message": "자신에게 강제 압류를 사용할 수 없습니다.",
                "event": None,
            }
        
        # 사거리 확인
        distance = self.game.calculate_distance(attacker, target)
        effective_range = attacker.get_effective_range()
        if effective_range < distance or distance > card.range:
            return {
                "success": False,
                "message": "거리가 너무 멉니다.",
                "event": None,
            }
        
        # PANIC 카드 제거 및 버리기
        removed_card = attacker.remove_card(card.id)
        if not removed_card:
            return {
                "success": False,
                "message": "카드를 제거할 수 없습니다.",
                "event": None,
            }
        self.card_manager.discard_card(removed_card)
        
        # 화수분 (수지 라파예트): 손패가 0장이 되면 2장 드로우
        self._trigger_suzy_if_needed(attacker)
        
        # 천청 방울 보유 여부 확인
        if getattr(attacker, "treasure", None) == "천청 방울":
            # 대상 손패에서 최대 2장 무작위 선택
            if target.get_hand_count() == 0:
                return {
                    "success": True,
                    "message": "대상 손패가 비어 있어 강탈할 카드가 없습니다.",
                    "event": None,
                }
            hand_cards = list(target.hand)
            sample_size = min(2, len(hand_cards))
            candidate_cards = random.sample(hand_cards, sample_size)
            
            # 서버 내부 컨텍스트 저장
            self.game.pending_action = {
                "type": "SELECT_STEAL_CARD",
                "attacker_id": attacker.id,
                "target_id": target.id,
                "cards": candidate_cards,
            }
            
            # 클라이언트에 후보 카드 ID만 노출
            self.game.required_response = {
                "type": "SELECT_STEAL_CARD",
                "source": "천청 방울",
                "targetId": target.id,
                "candidateCards": [{"id": c.id} for c in candidate_cards],
            }
            
            event_message = f"{attacker.name}이(가) 강제 압류를 사용했습니다. 천청 방울 효과로 강탈할 카드를 선택 중입니다."
            self.game.add_event(event_message, "action")
            
            return {
                "success": True,
                "message": "강제 압류를 사용했습니다. 강탈할 카드를 선택하세요.",
                "event": event_message,
            }
        
        # 기본 강제 압류: 대상 손패에서 무작위 카드 1장을 강탈
        if target.get_hand_count() == 0:
            return {
                "success": True,
                "message": "대상 손패가 비어 있어 강탈할 카드가 없습니다.",
                "event": None,
            }
        
        stolen_source_card = random.choice(target.hand)
        removed = target.remove_card(stolen_source_card.id)
        if removed:
            attacker.add_card(removed)
            event_message = f"{attacker.name}이(가) 강제 압류로 {target.name}의 손패에서 카드를 1장 강탈했습니다."
            self.game.add_event(event_message, "action")
            return {
                "success": True,
                "message": "강제 압류로 카드를 강탈했습니다.",
                "event": event_message,
            }
        
        return {
            "success": False,
            "message": "강탈할 카드를 찾을 수 없습니다.",
            "event": None,
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
        
        # 회피 카드인지 + 보물 효과 확인
        player_treasure = getattr(player, "treasure", None)
        has_calamity_treasure = player_treasure == "반전 금화"
        
        # 기본은 회피 카드만 가능하지만, 반전 금화가 있으면 정산 카드도 회피로 사용 가능
        if not card.is_missed() and not (has_calamity_treasure and card.is_bang()):
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
        
        # 낙인 인장 등으로 인해 여러 장의 회피가 필요할 수 있음
        self.game.pending_used_missed += 1
        required = max(1, self.game.pending_required_missed)
        used = self.game.pending_used_missed
        
        # 아직 충분히 회피하지 못한 경우: 대응 단계 유지
        if used < required:
            # 프론트에 남은 필요 회피 수 갱신
            if self.game.defending_player_id == player_id:
                self.game.required_response = {
                    "type": "RESPOND_ATTACK",
                    "targetId": player_id,
                    "requiredMissed": required,
                    "usedMissed": used,
                    "message": f"추가로 회피 카드가 더 필요합니다. (현재 {used}장 사용, 총 {required}장 필요)",
                }
            event_message = f"{player.name}이(가) 회피 카드를 사용했지만 추가 회피가 더 필요합니다."
            self.game.add_event(event_message, "action")
            return {
                "success": True,
                "message": "공격을 부분적으로 회피했습니다. 추가 회피가 필요합니다.",
                "event": event_message,
            }
        
        # 충분한 회피를 사용한 경우: 공격 완전 방어
        event_message = f"{player.name}이(가) 회피 카드를 사용하여 공격을 막았습니다."
        self.game.add_event(event_message, "action")
        
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
        
        # 비단 갑옷 (주르도네) + 만능 통보 (럭키 듀크) 판정:
        # 판정 문양이 '검'이면 자동 회피. 회피 성공 시 카드 1장 드로우.
        treasure = getattr(player, "treasure", None)
        if treasure == "비단 갑옷":
            success = self._perform_judgement(player, [Suit.SPADES])
            if success:
                # 회피 성공: 카드 1장 드로우
                cards = self.turn_manager.draw_cards_for_player(player.id, 1)
                if cards:
                    self.game.add_event(
                        f"{player.name}의 비단 갑옷 판정에 성공하여 공격을 회피하고 카드를 1장 드로우했습니다.",
                        "action",
                    )
                # 원래 플레이어의 턴으로 복귀
                if self.game.current_player_id:
                    self.turn_manager.return_to_play_phase()
                return {
                    "success": True,
                    "message": "비단 갑옷 효과로 공격을 회피했습니다.",
                    "event": self.game.last_event,
                }
            else:
                self.game.add_event(
                    f"{player.name}의 비단 갑옷 판정이 실패했습니다.",
                    "action",
                )
        
        # 피해 받기
        died = player.take_damage(1)
        
        # 이중 장부 (바트 캐시디): 재력 손실 시 턴당 최대 2회까지 1장 드로우
        if getattr(player, "treasure", None) == "이중 장부":
            counters = self.game.treasure_counters.setdefault(player.id, {})
            current_turn = self.game.turn_number
            last_turn = counters.get("_turn")
            if last_turn != current_turn:
                counters["_turn"] = current_turn
                counters["bart_damage_triggers"] = 0
            used = counters.get("bart_damage_triggers", 0)
            if used < 2:
                cards = self.turn_manager.draw_cards_for_player(player.id, 1)
                if cards:
                    counters["bart_damage_triggers"] = used + 1
                    self.game.add_event(
                        f"{player.name}의 이중 장부 효과로 카드 1장을 드로우했습니다.",
                        "action",
                    )
        
        # 응징의 패 (엘 링고): 나를 공격하여 피해를 입힌 상대의 손패에서 카드 1장 즉시 강탈
        attacker = (
            self.game.get_player(self.game.current_player_id)
            if self.game.current_player_id
            else None
        )
        if getattr(player, "treasure", None) == "응징의 패" and attacker and attacker.get_hand_count() > 0:
            stolen_source_card = random.choice(attacker.hand)
            removed = attacker.remove_card(stolen_source_card.id)
            if removed:
                player.add_card(removed)
                self.game.add_event(
                    f"{player.name}의 응징의 패 효과로 {attacker.name}의 손패에서 카드 1장을 강탈했습니다.",
                    "action",
                )
        
        if died:
            event_message = f"{player.name}이(가) 공격을 받아 재력이 0이 되어 사망했습니다."
        else:
            event_message = f"{player.name}이(가) 공격을 받아 재력이 {player.hp}로 감소했습니다."
        
        self.game.add_event(event_message, "action")
        
        # 원래 플레이어의 턴으로 복귀
        if self.game.current_player_id:
            self.turn_manager.return_to_play_phase()
        
        return {
            "success": True,
            "message": "공격을 받았습니다.",
            "event": event_message,
        }

    def handle_use_treasure(self, player_id: str, data: Dict) -> Dict:
        """
        능동형 보물 사용을 처리합니다.
        현재는 생명 장부 (시드 케첨)만 지원합니다.
        """
        player = self.game.get_player(player_id)
        if not player:
            return {
                "success": False,
                "message": "플레이어를 찾을 수 없습니다.",
                "event": None,
            }
        
        treasure_name = data.get("treasure")
        if treasure_name != "생명 장부" or getattr(player, "treasure", None) != "생명 장부":
            return {
                "success": False,
                "message": "생명 장부 보물을 가진 플레이어만 사용할 수 있습니다.",
                "event": None,
            }
        
        card_ids = data.get("card_ids") or []
        if len(card_ids) != 2:
            return {
                "success": False,
                "message": "서로 다른 문양의 카드 2장이 필요합니다.",
                "event": None,
            }
        
        # 카드 조회 및 문양 확인
        cards: List[Card] = []
        for cid in card_ids:
            c = player.get_card(cid)
            if not c:
                return {
                    "success": False,
                    "message": "지정한 카드를 찾을 수 없습니다.",
                    "event": None,
                }
            if not c.suit:
                return {
                    "success": False,
                    "message": "문양이 없는 카드는 사용할 수 없습니다.",
                    "event": None,
                }
            cards.append(c)
        
        if cards[0].suit == cards[1].suit:
            return {
                "success": False,
                "message": "서로 다른 문양의 카드 2장이 필요합니다.",
                "event": None,
            }
        
        # 카드 2장 버리기
        removed_cards: List[Card] = []
        for c in cards:
            removed = player.remove_card(c.id)
            if removed:
                removed_cards.append(removed)
        if removed_cards:
            self.card_manager.discard_cards(removed_cards)
        
        # 화수분 (수지 라파예트): 손패가 0장이 되면 2장 드로우
        self._trigger_suzy_if_needed(player)
        
        # 재력 회복 1
        old_hp = player.hp
        player.heal(1)
        
        event_message = f"{player.name}이(가) 생명 장부 효과로 서로 다른 문양의 카드를 2장 버리고 재력을 {old_hp}에서 {player.hp}로 회복했습니다."
        self.game.add_event(event_message, "action")
        
        return {
            "success": True,
            "message": "생명 장부 효과로 재력을 1 회복했습니다.",
            "event": event_message,
        }

    def handle_select_steal_card(self, player_id: str, data: Dict) -> Dict:
        """
        천청 방울 효과로 강탈할 카드를 선택하는 응답을 처리합니다.
        """
        ctx = self.game.pending_action or {}
        if ctx.get("type") != "SELECT_STEAL_CARD":
            return {
                "success": False,
                "message": "선택할 강탈 액션이 없습니다.",
                "event": None,
            }
        
        if ctx.get("attacker_id") != player_id:
            return {
                "success": False,
                "message": "강탈 카드를 선택할 권한이 없습니다.",
                "event": None,
            }
        
        target_id = ctx.get("target_id")
        card_id = data.get("card_id")
        if not card_id:
            return {
                "success": False,
                "message": "선택할 카드 ID가 필요합니다.",
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
        
        # 대상 손패에서 해당 카드를 제거하고 공격자에게 추가
        removed = target.remove_card(card_id)
        if not removed:
            return {
                "success": False,
                "message": "대상 손패에서 선택한 카드를 찾을 수 없습니다.",
                "event": None,
            }
        attacker.add_card(removed)
        
        # 컨텍스트 정리
        self.game.pending_action = None
        self.game.required_response = None
        
        event_message = f"{attacker.name}이(가) 천청 방울 효과로 {target.name}의 손패에서 카드를 1장 강탈했습니다."
        self.game.add_event(event_message, "action")
        
        return {
            "success": True,
            "message": "강탈할 카드를 선택했습니다.",
            "event": event_message,
        }

    def handle_select_draw_order(self, player_id: str, data: Dict) -> Dict:
        """
        우선 전표 효과로 드로우/덱 위/덱 아래 배치를 선택하는 응답을 처리합니다.
        """
        ctx = self.game.pending_action or {}
        if ctx.get("type") != "SELECT_DRAW_ORDER":
            return {
                "success": False,
                "message": "선택할 드로우 액션이 없습니다.",
                "event": None,
            }
        
        if ctx.get("player_id") != player_id:
            return {
                "success": False,
                "message": "드로우 순서를 선택할 권한이 없습니다.",
                "event": None,
            }
        
        take_id = data.get("take_card_id")
        top_id = data.get("top_card_id")
        bottom_id = data.get("bottom_card_id")
        if not take_id or not top_id or not bottom_id:
            return {
                "success": False,
                "message": "획득/위/아래 배치에 사용할 카드 ID가 모두 필요합니다.",
                "event": None,
            }
        
        cards: List[Card] = ctx.get("cards") or []
        card_map = {c.id: c for c in cards}
        if not (take_id in card_map and top_id in card_map and bottom_id in card_map):
            return {
                "success": False,
                "message": "선택한 카드 ID가 유효하지 않습니다.",
                "event": None,
            }
        if len({take_id, top_id, bottom_id}) != len(cards):
            return {
                "success": False,
                "message": "각 카드는 서로 다른 역할로 한 번씩만 사용해야 합니다.",
                "event": None,
            }
        
        player = self.game.get_player(player_id)
        if not player:
            return {
                "success": False,
                "message": "플레이어를 찾을 수 없습니다.",
                "event": None,
            }
        
        # 1장 손패로 획득
        player.add_card(card_map[take_id])
        
        # 1장은 덱 맨 위, 1장은 덱 맨 아래
        # 덱 맨 위: 리스트 앞쪽에 삽입
        self.card_manager.deck.insert(0, card_map[top_id])
        # 덱 맨 아래: 헬퍼 사용
        self.card_manager.put_card_to_bottom(card_map[bottom_id])
        
        # 컨텍스트 정리
        self.game.pending_action = None
        self.game.required_response = None
        
        # 이벤트 및 턴 상태 갱신
        self.game.add_event(
            f"{player.name}이(가) 우선 전표 효과로 카드 1장을 획득하고 나머지 2장을 덱 위/아래로 배치했습니다.",
            "action",
        )
        # 드로우 단계를 마치고 카드 사용 단계로 이동
        self.game.set_turn_state(TurnState.PLAY_CARD)
        
        return {
            "success": True,
            "message": "우선 전표 효과로 드로우/배치를 완료했습니다.",
            "event": self.game.last_event,
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
            player = self.game.get_player(player_id)
            event_message = f"{player.name}의 턴이 종료되었습니다."
            self.game.add_event(event_message, "notification")
            return {
                "success": True,
                "message": "턴이 종료되었습니다.",
                "event": event_message,
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
            
            # 반전 금화 보유 시 정산 카드도 회피로 사용할 수 있음
            player_treasure = getattr(player, "treasure", None)
            has_calamity_treasure = player_treasure == "반전 금화"
            if not card.is_missed() and not (has_calamity_treasure and card.is_bang()):
                return False, "회피 카드만 사용할 수 있습니다."
        
        elif action_type == ActionType.END_TURN:
            if not self.turn_manager.can_end_turn(player_id):
                return False, "턴을 종료할 수 없는 상태입니다."
        
        elif action_type == ActionType.USE_TREASURE:
            # 보물 사용 공통 검증 (현재는 생명 장부 전용)
            treasure_name = data.get("treasure")
            if treasure_name != "생명 장부":
                return False, "지원하지 않는 보물 사용입니다."
            card_ids = data.get("card_ids") or []
            if len(card_ids) != 2:
                return False, "카드 2장이 필요합니다."
        
        elif action_type in (ActionType.SELECT_STEAL_CARD, ActionType.SELECT_DRAW_ORDER):
            # 선택형 응답은 세부 검증을 각 핸들러에서 수행
            pass
        
        return True, None

