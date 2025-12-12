"""
AI 플레이어 추가 기능 테스트 스크립트
"""

import asyncio
import json
import websockets
from typing import Optional


async def test_ai_player_addition():
    """AI 플레이어 추가 기능 테스트"""
    
    # 테스트 설정
    game_id = "test_game_ai_001"
    player_name = "TestPlayer"
    base_url = "ws://localhost:8080"
    
    print("=" * 60)
    print("AI 플레이어 추가 기능 테스트")
    print("=" * 60)
    print()
    
    try:
        # 1. 로비 연결
        print(f"[1단계] 로비 연결 중...")
        print(f"   URL: {base_url}/lobby/{game_id}?player={player_name}")
        
        uri = f"{base_url}/lobby/{game_id}?player={player_name}"
        async with websockets.connect(uri) as websocket:
            print("   [OK] WebSocket 연결 성공")
            print()
            
            # 2. CONNECTION_ESTABLISHED 메시지 수신
            print("[2단계] 연결 확인 메시지 수신 대기...")
            response = await websocket.recv()
            message = json.loads(response)
            
            if message.get("type") == "CONNECTION_ESTABLISHED":
                player_id = message.get("player_id")
                print(f"   [OK] 연결 확인 메시지 수신")
                print(f"   플레이어 ID: {player_id}")
                print(f"   게임 ID: {message.get('game_id')}")
                print()
            else:
                print(f"   [ERROR] 예상하지 못한 메시지: {message}")
                return
            
            # 3. GAME_STATE_UPDATE 메시지 수신 (자동 참가 후)
            print("[3단계] 게임 상태 업데이트 메시지 수신 대기...")
            response = await websocket.recv()
            message = json.loads(response)
            
            if message.get("type") == "GAME_STATE_UPDATE":
                players = message.get("players", [])
                print(f"   [OK] 게임 상태 업데이트 수신")
                print(f"   현재 플레이어 수: {len(players)}")
                print(f"   Phase: {message.get('phase')}")
                print(f"   플레이어 목록:")
                for p in players:
                    print(f"     - {p.get('name')} (ID: {p.get('id')}, isBot: {p.get('isBot', False)})")
                print()
            else:
                print(f"   [WARNING] 예상하지 못한 메시지: {message.get('type')}")
            
            # 4. AI 플레이어 추가 요청
            print("[4단계] AI 플레이어 추가 요청...")
            ai_request = {
                "type": "ADD_AI_PLAYER",
                "count": 3,
                "difficulty": "medium"
            }
            await websocket.send(json.dumps(ai_request))
            print(f"   전송 메시지: {json.dumps(ai_request, ensure_ascii=False, indent=2)}")
            print()
            
            # 5. AI 플레이어 추가 응답 및 게임 상태 업데이트 수신
            print("[5단계] AI 플레이어 추가 응답 대기...")
            
            # 여러 메시지를 받을 수 있으므로 순서에 관계없이 처리
            action_response = None
            game_state_update = None
            
            # 최대 2개의 메시지 수신 (ACTION_RESPONSE, GAME_STATE_UPDATE)
            for _ in range(2):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message = json.loads(response)
                    
                    if message.get("type") == "ACTION_RESPONSE":
                        action_response = message
                    elif message.get("type") == "GAME_STATE_UPDATE":
                        game_state_update = message
                except asyncio.TimeoutError:
                    break
            
            # ACTION_RESPONSE 확인
            if action_response:
                data = action_response.get("data", {})
                if data.get("success"):
                    print(f"   [OK] AI 플레이어 추가 성공")
                    print(f"   메시지: {data.get('message')}")
                    print(f"   추가된 수: {data.get('added_count')}")
                    print()
                else:
                    print(f"   [ERROR] AI 플레이어 추가 실패")
                    print(f"   메시지: {data.get('message')}")
                    return
            else:
                print(f"   [WARNING] ACTION_RESPONSE 메시지를 받지 못했습니다.")
            
            # 6. GAME_STATE_UPDATE 메시지 확인 (AI 추가 후)
            print("[6단계] AI 추가 후 게임 상태 업데이트 확인...")
            
            # 이미 받았으면 사용, 아니면 추가로 받기
            if not game_state_update:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message = json.loads(response)
                    if message.get("type") == "GAME_STATE_UPDATE":
                        game_state_update = message
                except asyncio.TimeoutError:
                    print(f"   [WARNING] GAME_STATE_UPDATE 메시지를 받지 못했습니다.")
                    return
            
            if game_state_update:
                message = game_state_update
            
            if message.get("type") == "GAME_STATE_UPDATE":
                players = message.get("players", [])
                print(f"   [OK] 게임 상태 업데이트 수신")
                print(f"   현재 플레이어 수: {len(players)}")
                print(f"   Phase: {message.get('phase')}")
                print()
                print(f"   플레이어 목록:")
                for p in players:
                    bot_status = "[AI]" if p.get("isBot") else "[Human]"
                    print(f"     - {bot_status} {p.get('name')} (ID: {p.get('id')[:8]}..., isBot: {p.get('isBot')})")
                print()
                
                # AI 플레이어 확인
                ai_players = [p for p in players if p.get("isBot")]
                human_players = [p for p in players if not p.get("isBot")]
                
                print(f"   [통계]")
                print(f"     - 총 플레이어: {len(players)}명")
                print(f"     - 인간 플레이어: {len(human_players)}명")
                print(f"     - AI 플레이어: {len(ai_players)}명")
                print()
                
                if len(ai_players) > 0:
                    print("   [OK] AI 플레이어 추가 테스트 성공!")
                else:
                    print("   [ERROR] AI 플레이어가 추가되지 않았습니다.")
            else:
                print(f"   [WARNING] 예상하지 못한 메시지 타입: {message.get('type')}")
            
            # 7. 추가 테스트: 최대 플레이어 수 초과 시도
            print()
            print("[7단계] 최대 플레이어 수 초과 테스트...")
            ai_request = {
                "type": "ADD_AI_PLAYER",
                "count": 10,  # 최대값 초과
                "difficulty": "medium"
            }
            await websocket.send(json.dumps(ai_request))
            print(f"   전송 메시지: {json.dumps(ai_request, ensure_ascii=False, indent=2)}")
            
            response = await websocket.recv()
            message = json.loads(response)
            
            if message.get("type") == "ACTION_RESPONSE":
                data = message.get("data", {})
                if not data.get("success"):
                    print(f"   [OK] 에러 처리 정상 작동")
                    print(f"   에러 메시지: {data.get('message')}")
                else:
                    print(f"   [ERROR] 에러가 발생해야 하는데 성공했습니다.")
            else:
                print(f"   [WARNING] 예상하지 못한 메시지 타입: {message.get('type')}")
            
            print()
            print("=" * 60)
            print("테스트 완료")
            print("=" * 60)
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"   [ERROR] 연결이 종료되었습니다: {e}")
    except Exception as e:
        print(f"   [ERROR] 에러 발생: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("서버 연결 테스트를 시작합니다...")
    print("서버가 실행 중인지 확인하세요: http://localhost:8080/health")
    print()
    
    try:
        asyncio.run(test_ai_player_addition())
    except KeyboardInterrupt:
        print("\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n테스트 실행 중 에러 발생: {e}")
        import traceback
        traceback.print_exc()

