"""
AI 플레이어 추가 기능 간단 테스트
"""

import asyncio
import json
import websockets
import sys
import io

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


async def simple_test():
    """간단한 AI 플레이어 추가 테스트"""
    
    game_id = "test_simple_001"
    player_name = "TestUser"
    
    try:
        uri = f"ws://localhost:8080/lobby/{game_id}?player={player_name}"
        print(f"연결 중: {uri}")
        
        async with websockets.connect(uri) as ws:
            print("[OK] 연결 성공")
            
            # 첫 메시지 (CONNECTION_ESTABLISHED)
            msg1 = json.loads(await ws.recv())
            print(f"메시지 1: {msg1.get('type')}")
            
            # 두 번째 메시지 (GAME_STATE_UPDATE)
            msg2 = json.loads(await ws.recv())
            print(f"메시지 2: {msg2.get('type')}, 플레이어 수: {len(msg2.get('players', []))}")
            
            # AI 플레이어 추가 요청
            ai_req = {"type": "ADD_AI_PLAYER", "count": 2, "difficulty": "medium"}
            await ws.send(json.dumps(ai_req))
            print(f"[OK] AI 추가 요청 전송: count=2")
            
            # 응답 수신 (순서 무관)
            for i in range(3):
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=1.0))
                    msg_type = msg.get('type')
                    print(f"응답 {i+1}: {msg_type}")
                    
                    if msg_type == "ACTION_RESPONSE":
                        data = msg.get('data', {})
                        print(f"  성공: {data.get('success')}")
                        print(f"  메시지: {data.get('message')}")
                        print(f"  추가된 수: {data.get('added_count')}")
                    elif msg_type == "GAME_STATE_UPDATE":
                        players = msg.get('players', [])
                        ai_count = sum(1 for p in players if p.get('isBot'))
                        print(f"  플레이어 수: {len(players)}")
                        print(f"  AI 플레이어 수: {ai_count}")
                        if ai_count > 0:
                            print("[OK] AI 플레이어 추가 성공!")
                            return
                except asyncio.TimeoutError:
                    break
            
            print("[WARNING] 예상한 응답을 받지 못했습니다.")
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(simple_test())

