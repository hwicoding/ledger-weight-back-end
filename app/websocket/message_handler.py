"""
메시지 핸들러 (Message Handler)

WebSocket 메시지를 처리하고 게임 상태를 업데이트합니다.
"""

import json
from typing import Dict, Optional
from app.models.game import Game
from app.game.game_manager import GameManager
from app.game.turn_manager import TurnManager
from app.game.action_handler import ActionHandler
from app.websocket.connection_manager import ConnectionManager
from app.utils.constants import ActionType, GameState


class MessageHandler:
    """
    메시지 핸들러 클래스
    
    WebSocket 메시지를 처리하고 게임 로직과 통신합니다.
    """
    
    def __init__(
        self,
        game_manager: GameManager,
        connection_manager: ConnectionManager,
    ):
        """
        메시지 핸들러 초기화
        
        Args:
            game_manager: GameManager 인스턴스
            connection_manager: ConnectionManager 인스턴스
        """
        self.game_manager = game_manager
        self.connection_manager = connection_manager
    
    async def handle_message(self, player_id: str, message: dict) -> Dict:
        """
        플레이어로부터 받은 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: 받은 메시지
            
        Returns:
            처리 결과
        """
        message_type = message.get("type")
        
        if message_type == "PLAYER_ACTION":
            return await self.handle_player_action(player_id, message)
        elif message_type == "JOIN_GAME":
            return await self.handle_join_game(player_id, message)
        elif message_type == "GET_GAME_STATE":
            return await self.handle_get_game_state(player_id, message)
        else:
            return {
                "success": False,
                "message": f"지원하지 않는 메시지 타입: {message_type}",
            }
    
    async def handle_player_action(self, player_id: str, message: dict) -> Dict:
        """
        플레이어 액션 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "PLAYER_ACTION",
                "action": {
                    "type": "USE_CARD" | "RESPOND_ATTACK" | "END_TURN",
                    "cardId": "string (optional, USE_CARD 시 필수)",
                    "targetId": "string (optional, USE_CARD 시 타겟 필요 시 필수)",
                    "response": "evade" | "give_up" (RESPOND_ATTACK 시 필수)
                }
            }
            
        Returns:
            처리 결과
        """
        game_id = self.connection_manager.get_player_game(player_id)
        if not game_id:
            return {
                "success": False,
                "message": "플레이어가 게임에 참여하지 않았습니다.",
            }
        
        game = self.game_manager.get_game(game_id)
        if not game:
            return {
                "success": False,
                "message": "게임을 찾을 수 없습니다.",
            }
        
        # 게임 로직 컴포넌트 생성
        from app.game.card_manager import CardManager
        from app.game.turn_manager import TurnManager
        from app.game.action_handler import ActionHandler
        
        card_manager = self.game_manager.get_card_manager(game_id)
        turn_manager = TurnManager(game, card_manager)
        action_handler = ActionHandler(game, turn_manager, card_manager)
        
        # 새로운 메시지 형식 파싱
        action = message.get("action", {})
        if not action:
            return {
                "success": False,
                "message": "액션 정보가 필요합니다.",
            }
        
        action_type_str = action.get("type")
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            return {
                "success": False,
                "message": f"잘못된 액션 타입: {action_type_str}",
            }
        
        # 액션 타입별 데이터 변환 (기존 ActionHandler 형식으로)
        if action_type == ActionType.USE_CARD:
            data = {
                "card_id": action.get("cardId"),
                "target_id": action.get("targetId"),
            }
            result = action_handler.handle_action(action_type, player_id, data)
        elif action_type == ActionType.RESPOND_ATTACK:
            response = action.get("response")
            if response == "evade":
                # 회피 카드 사용 - cardId 필요
                data = {
                    "card_id": action.get("cardId"),
                }
                result = action_handler.handle_action(action_type, player_id, data)
            elif response == "give_up":
                # 포기 - handle_respond_attack_failed 호출
                result = action_handler.handle_respond_attack_failed(player_id)
            else:
                return {
                    "success": False,
                    "message": f"잘못된 응답 타입: {response}",
                }
        elif action_type == ActionType.END_TURN:
            data = {}
            result = action_handler.handle_action(action_type, player_id, data)
        else:
            return {
                "success": False,
                "message": f"지원하지 않는 액션 타입: {action_type_str}",
            }
        
        # 게임 상태 업데이트 전송
        if result.get("success"):
            await self.broadcast_game_state(game_id)
        
        # 승리 조건 체크
        win_info = self.game_manager.check_win_condition(game_id)
        if win_info:
            await self.broadcast_game_state(game_id)
            await self.broadcast_win_info(game_id, win_info)
        
        return result
    
    async def handle_join_game(self, player_id: str, message: dict) -> Dict:
        """
        게임 참여 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "JOIN_GAME",
                "game_id": str,
                "player_name": str
            }
            
        Returns:
            처리 결과
        """
        game_id = message.get("game_id")
        player_name = message.get("player_name", f"Player_{player_id}")
        
        if not game_id:
            return {
                "success": False,
                "message": "게임 ID가 필요합니다.",
            }
        
        # 게임 조회 또는 생성
        game = self.game_manager.get_game(game_id)
        if not game:
            game = self.game_manager.create_game(game_id)
        
        # 플레이어 추가
        success = self.game_manager.add_player_to_game(
            game_id, player_id, player_name
        )
        
        if not success:
            return {
                "success": False,
                "message": "게임에 참여할 수 없습니다.",
            }
        
        # 연결 관리자에 등록
        self.connection_manager.register_player_to_game(player_id, game_id)
        
        # 게임 상태 전송
        await self.send_game_state_to_player(player_id, game_id)
        
        # 다른 플레이어들에게 알림
        await self.broadcast_game_state(game_id)
        
        return {
            "success": True,
            "message": "게임에 참여했습니다.",
            "game_id": game_id,
        }
    
    async def handle_get_game_state(self, player_id: str, message: dict) -> Dict:
        """
        게임 상태 조회 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "GET_GAME_STATE"
            }
            
        Returns:
            처리 결과
        """
        game_id = self.connection_manager.get_player_game(player_id)
        if not game_id:
            return {
                "success": False,
                "message": "플레이어가 게임에 참여하지 않았습니다.",
            }
        
        await self.send_game_state_to_player(player_id, game_id)
        
        return {
            "success": True,
            "message": "게임 상태를 전송했습니다.",
        }
    
    async def send_game_state_to_player(self, player_id: str, game_id: str) -> bool:
        """
        플레이어에게 게임 상태를 전송합니다.
        
        Args:
            player_id: 플레이어 ID
            game_id: 게임 ID
            
        Returns:
            전송 성공 여부
        """
        game_state = self.game_manager.get_game_state_dict(game_id, player_id)
        if not game_state:
            return False
        
        # 프론트엔드 요청 형식으로 메시지 구성
        message = {
            "type": "GAME_STATE_UPDATE",
            **game_state,  # gameId, players, currentTurn, turnState, events, phase
        }
        
        return await self.connection_manager.send_personal_message(message, player_id)
    
    async def broadcast_game_state(self, game_id: str) -> int:
        """
        게임의 모든 플레이어에게 게임 상태를 브로드캐스트합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            전송 성공한 플레이어 수
        """
        game = self.game_manager.get_game(game_id)
        if not game:
            return 0
        
        player_ids = self.connection_manager.get_game_players(game_id)
        success_count = 0
        
        for player_id in list(player_ids):
            if await self.send_game_state_to_player(player_id, game_id):
                success_count += 1
        
        return success_count
    
    async def broadcast_win_info(self, game_id: str, win_info: dict) -> int:
        """
        승리 정보를 브로드캐스트합니다.
        
        Args:
            game_id: 게임 ID
            win_info: 승리 정보
            
        Returns:
            전송 성공한 플레이어 수
        """
        message = {
            "type": "GAME_END",
            "data": win_info,
        }
        
        return await self.connection_manager.broadcast_to_game(message, game_id)

