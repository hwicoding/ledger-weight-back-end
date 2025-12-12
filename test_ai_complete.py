"""
AI 플레이어 추가 기능 완전 테스트
- AI 추가 기능 확인
- 최소 인원(4명)까지 AI 추가
- 게임 시작 가능 여부 확인
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


async def complete_test():
    """완전한 AI 플레이어 추가 및 게임 시작 테스트"""
    
    game_id = "test_complete_001"
    player_name = "TestUser"
    MIN_PLAYERS = 4
    
    try:
        uri = f"ws://localhost:8080/lobby/{game_id}?player={player_name}"
        print("=" * 60)
        print("AI 플레이어 추가 완전 테스트")
        print("=" * 60)
        print(f"연결 중: {uri}")
        
        async with websockets.connect(uri) as ws:
            print("[OK] 연결 성공\n")
            
            # 1. 초기 연결 메시지 수신
            msg1 = json.loads(await ws.recv())
            print(f"[1] {msg1.get('type')}: 플레이어 ID = {msg1.get('player_id')[:8]}...")
            
            msg2 = json.loads(await ws.recv())
            players = msg2.get('players', [])
            print(f"[2] {msg2.get('type')}: 현재 플레이어 수 = {len(players)}명")
            print(f"    - {players[0].get('name')} (isBot: {players[0].get('isBot')})")
            print()
            
            # 2. 최소 인원까지 AI 추가 (본인 1명 + AI 3명 = 4명)
            print(f"[3] 최소 인원({MIN_PLAYERS}명)까지 AI 추가 중...")
            ai_req = {"type": "ADD_AI_PLAYER", "count": 3, "difficulty": "medium"}
            await ws.send(json.dumps(ai_req))
            print(f"    요청: AI {ai_req['count']}명 추가")
            
            # 응답 수신
            responses = []
            for i in range(3):
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=2.0))
                    responses.append(msg)
                    msg_type = msg.get('type')
                    if msg_type == "ACTION_RESPONSE":
                        data = msg.get('data', {})
                        if data.get('success'):
                            print(f"    [OK] AI 추가 성공: {data.get('added_count')}명 추가됨")
                        else:
                            print(f"    [ERROR] AI 추가 실패: {data.get('message')}")
                            return
                    elif msg_type == "GAME_STATE_UPDATE":
                        players = msg.get('players', [])
                        ai_count = sum(1 for p in players if p.get('isBot'))
                        human_count = sum(1 for p in players if not p.get('isBot'))
                        print(f"    게임 상태 업데이트: 총 {len(players)}명 (인간 {human_count}명 + AI {ai_count}명)")
                except asyncio.TimeoutError:
                    break
            
            # 최종 플레이어 수 확인
            final_state = [r for r in responses if r.get('type') == 'GAME_STATE_UPDATE']
            if final_state:
                final_players = final_state[-1].get('players', [])
                print(f"\n[4] 최종 플레이어 상태:")
                for p in final_players:
                    bot_mark = "[AI]" if p.get('isBot') else "[Human]"
                    print(f"    - {bot_mark} {p.get('name')} (isBot: {p.get('isBot')})")
                print(f"    총 {len(final_players)}명")
                
                if len(final_players) >= MIN_PLAYERS:
                    print(f"\n[OK] 최소 인원({MIN_PLAYERS}명) 충족! 게임 시작 가능")
                else:
                    print(f"\n[ERROR] 최소 인원({MIN_PLAYERS}명) 미달: 현재 {len(final_players)}명")
                    return
            
            # 3. 게임 시작 시도
            print(f"\n[5] 게임 시작 시도...")
            start_req = {"type": "START_GAME"}
            await ws.send(json.dumps(start_req))
            
            # 게임 시작 응답 수신
            for i in range(3):
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=2.0))
                    msg_type = msg.get('type')
                    
                    if msg_type == "ACTION_RESPONSE":
                        data = msg.get('data', {})
                        if data.get('success'):
                            print(f"    [OK] 게임 시작 성공!")
                            print(f"    메시지: {data.get('message')}")
                        else:
                            print(f"    [ERROR] 게임 시작 실패: {data.get('message')}")
                            return
                    elif msg_type == "GAME_STATE_UPDATE":
                        phase = msg.get('phase')
                        players = msg.get('players', [])
                        print(f"    게임 상태: phase = {phase}, 플레이어 수 = {len(players)}명")
                        if phase == "playing":
                            print(f"    [OK] 게임이 정상적으로 시작되었습니다!")
                            return
                except asyncio.TimeoutError:
                    break
            
            print("\n" + "=" * 60)
            print("테스트 완료")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(complete_test())

