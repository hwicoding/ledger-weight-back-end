"""
게임 매니저 (Game Manager)

게임의 생성, 초기화, 상태 관리, 승리 조건 체크 등을 담당합니다.
"""

import uuid
import random
from typing import List, Dict, Optional
from app.models.game import Game
from app.models.player import Player
from app.models.card import Card
from app.game.card_manager import CardManager
from app.utils.constants import (
    GameState,
    TurnState,
    Role as RoleEnum,
    MIN_PLAYERS,
    MAX_PLAYERS,
)


class GameManager:
    """
    게임 매니저 클래스
    
    게임 인스턴스의 생성, 관리, 상태 업데이트를 담당합니다.
    """
    
    def __init__(self):
        """게임 매니저 초기화"""
        self.games: Dict[str, Game] = {}  # 게임 ID -> Game 인스턴스
        self.card_managers: Dict[str, CardManager] = {}  # 게임 ID -> CardManager
    
    def create_game(self, game_id: Optional[str] = None) -> Game:
        """
        새 게임을 생성합니다.
        
        Args:
            game_id: 게임 ID (없으면 자동 생성)
            
        Returns:
            생성된 Game 인스턴스
        """
        if game_id is None:
            game_id = f"game_{uuid.uuid4().hex[:8]}"
        
        if game_id in self.games:
            raise ValueError(f"게임 ID {game_id}가 이미 존재합니다.")
        
        # 게임 생성
        game = Game(
            id=game_id,
            state=GameState.WAITING,
            turn_state=TurnState.DRAW,
        )
        
        # 카드 관리자 생성
        card_manager = CardManager()
        
        # 저장
        self.games[game_id] = game
        self.card_managers[game_id] = card_manager
        
        return game
    
    def add_player_to_game(
        self,
        game_id: str,
        player_id: str,
        player_name: str,
    ) -> bool:
        """
        게임에 플레이어를 추가합니다.
        
        Args:
            game_id: 게임 ID
            player_id: 플레이어 ID
            player_name: 플레이어 이름
            
        Returns:
            추가 성공 여부
        """
        game = self.get_game(game_id)
        if not game:
            return False
        
        if game.state != GameState.WAITING:
            return False  # 게임이 이미 시작되었거나 종료됨
        
        if len(game.players) >= MAX_PLAYERS:
            return False  # 최대 인원 초과
        
        # 이미 존재하는 플레이어인지 확인
        if any(p.id == player_id for p in game.players):
            return False
        
        # 플레이어 생성 (역할은 아직 배정하지 않음)
        position = len(game.players)
        player = Player.create(
            player_id=player_id,
            name=player_name,
            role=RoleEnum.SHERIFF,  # 임시 역할 (게임 시작 시 재배정)
            position=position,
        )
        
        game.add_player(player)
        return True
    
    def start_game(self, game_id: str) -> bool:
        """
        게임을 시작합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            시작 성공 여부
        """
        game = self.get_game(game_id)
        if not game:
            return False
        
        if game.state != GameState.WAITING:
            return False  # 이미 시작되었거나 종료됨
        
        if len(game.players) < MIN_PLAYERS:
            return False  # 최소 인원 미달
        
        # 역할 배정
        self._assign_roles(game)
        
        # 카드 덱 생성 및 셔플
        card_manager = self.card_managers[game_id]
        deck = card_manager.create_full_deck_and_shuffle()
        game.deck = deck
        
        # 초기 카드 분배
        self._deal_initial_cards(game, card_manager)
        
        # 게임 상태 변경
        game.state = GameState.IN_PROGRESS
        game.turn_number = 1
        
        # 첫 번째 플레이어 설정 (상단주가 첫 턴)
        sheriff = next((p for p in game.players if p.role.is_sheriff), None)
        if sheriff:
            game.current_player_id = sheriff.id
            game.set_current_player(sheriff.id)
            game.set_turn_state(TurnState.DRAW)
        
        return True
    
    def _assign_roles(self, game: Game) -> None:
        """
        플레이어들에게 역할을 배정합니다.
        
        Args:
            game: 게임 인스턴스
        """
        player_count = len(game.players)
        roles: List[RoleEnum] = []
        
        # 플레이어 수에 따른 역할 구성
        if player_count == 4:
            roles = [
                RoleEnum.SHERIFF,
                RoleEnum.DEPUTY,
                RoleEnum.OUTLAW,
                RoleEnum.RENEGADE,
            ]
        elif player_count == 5:
            roles = [
                RoleEnum.SHERIFF,
                RoleEnum.DEPUTY,
                RoleEnum.OUTLAW,
                RoleEnum.OUTLAW,
                RoleEnum.RENEGADE,
            ]
        elif player_count == 6:
            roles = [
                RoleEnum.SHERIFF,
                RoleEnum.DEPUTY,
                RoleEnum.DEPUTY,
                RoleEnum.OUTLAW,
                RoleEnum.OUTLAW,
                RoleEnum.RENEGADE,
            ]
        elif player_count == 7:
            roles = [
                RoleEnum.SHERIFF,
                RoleEnum.DEPUTY,
                RoleEnum.DEPUTY,
                RoleEnum.OUTLAW,
                RoleEnum.OUTLAW,
                RoleEnum.OUTLAW,
                RoleEnum.RENEGADE,
            ]
        else:
            # 기본 구성 (4명 기준)
            roles = [
                RoleEnum.SHERIFF,
                RoleEnum.DEPUTY,
                RoleEnum.OUTLAW,
                RoleEnum.RENEGADE,
            ]
            # 나머지는 적도 세력으로 채움
            while len(roles) < player_count:
                roles.append(RoleEnum.OUTLAW)
        
        # 역할 셔플 (상단주 제외)
        roles_to_shuffle = [r for r in roles if r != RoleEnum.SHERIFF]
        random.shuffle(roles_to_shuffle)
        
        # 상단주는 첫 번째 플레이어
        final_roles = [RoleEnum.SHERIFF] + roles_to_shuffle
        
        # 플레이어에게 역할 배정
        for i, player in enumerate(game.players):
            from app.models.role import Role
            player.role = Role(final_roles[i])
            # 역할에 따른 초기 재력 재설정
            from app.utils.constants import INITIAL_HP
            initial_hp = INITIAL_HP[final_roles[i]]
            player.hp = initial_hp
            player.max_hp = initial_hp
    
    def _deal_initial_cards(self, game: Game, card_manager: CardManager) -> None:
        """
        게임 시작 시 초기 카드를 분배합니다.
        
        Args:
            game: 게임 인스턴스
            card_manager: 카드 관리자
        """
        for player in game.players:
            # 플레이어 수에 따른 초기 카드 수
            initial_cards = 4 if len(game.players) <= 4 else 5
            
            # 카드 분배
            cards = card_manager.draw_cards(initial_cards)
            for card in cards:
                player.add_card(card)
    
    def get_game(self, game_id: str) -> Optional[Game]:
        """
        게임을 조회합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            Game 인스턴스 (없으면 None)
        """
        return self.games.get(game_id)
    
    def get_card_manager(self, game_id: str) -> Optional[CardManager]:
        """
        카드 관리자를 조회합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            CardManager 인스턴스 (없으면 None)
        """
        return self.card_managers.get(game_id)
    
    def remove_game(self, game_id: str) -> bool:
        """
        게임을 제거합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            제거 성공 여부
        """
        if game_id in self.games:
            del self.games[game_id]
            if game_id in self.card_managers:
                del self.card_managers[game_id]
            return True
        return False
    
    def check_win_condition(self, game_id: str) -> Optional[Dict[str, any]]:
        """
        승리 조건을 체크합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            승리 정보 (승리자가 없으면 None)
            {
                "winner_id": str,
                "winner_role": str,
                "reason": str
            }
        """
        game = self.get_game(game_id)
        if not game or game.state != GameState.IN_PROGRESS:
            return None
        
        alive_players = game.get_alive_players()
        
        if len(alive_players) == 0:
            # 모두 사망 (무승부)
            game.state = GameState.FINISHED
            return {
                "winner_id": None,
                "winner_role": None,
                "reason": "모든 플레이어가 사망했습니다.",
            }
        
        # 상단주 확인
        sheriff = next((p for p in alive_players if p.role.is_sheriff), None)
        
        if not sheriff:
            # 상단주 사망 - 적도 세력 승리
            outlaws = [p for p in alive_players if p.role.is_outlaw]
            if outlaws:
                game.state = GameState.FINISHED
                return {
                    "winner_id": outlaws[0].id,
                    "winner_role": "적도 세력",
                    "reason": "상단주가 사망했습니다.",
                }
        else:
            # 상단주 생존
            # 적도 세력이 모두 사망했는지 확인
            outlaws = [p for p in alive_players if p.role.is_outlaw]
            
            if not outlaws:
                # 적도 세력 모두 사망
                # 야망가가 혼자 남았는지 확인
                renegades = [p for p in alive_players if p.role.is_renegade]
                
                if len(renegades) == 1 and len(alive_players) == 2:
                    # 야망가가 상단주와 1대1 상황 - 야망가 승리
                    game.state = GameState.FINISHED
                    return {
                        "winner_id": renegades[0].id,
                        "winner_role": "야망가",
                        "reason": "야망가가 마지막까지 생존했습니다.",
                    }
                else:
                    # 상단주 팀 승리
                    game.state = GameState.FINISHED
                    return {
                        "winner_id": sheriff.id,
                        "winner_role": "상단주",
                        "reason": "상단주 팀이 승리했습니다.",
                    }
        
        return None  # 아직 승리 조건 미충족
    
    def get_game_state_dict(self, game_id: str, player_id: Optional[str] = None) -> Optional[dict]:
        """
        게임 상태를 딕셔너리로 반환합니다 (WebSocket 전송용).
        
        Args:
            game_id: 게임 ID
            player_id: 조회하는 플레이어 ID (자신의 핸드는 보이고, 다른 플레이어는 숨김)
            
        Returns:
            게임 상태 딕셔너리
        """
        game = self.get_game(game_id)
        if not game:
            return None
        
        return game.to_dict(player_id=player_id)
    
    def list_games(self) -> List[Dict[str, any]]:
        """
        모든 게임 목록을 반환합니다.
        
        Returns:
            게임 목록
        """
        return [
            {
                "id": game.id,
                "state": game.state.value,
                "player_count": len(game.players),
                "max_players": MAX_PLAYERS,
            }
            for game in self.games.values()
        ]

