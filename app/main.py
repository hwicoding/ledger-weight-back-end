"""
FastAPI 애플리케이션 진입점
"""

import json
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.game.game_manager import GameManager
from app.websocket.connection_manager import ConnectionManager
from app.websocket.message_handler import MessageHandler

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="장부의 무게 - WebSocket 기반 실시간 카드 게임 서버",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 인스턴스
game_manager = GameManager()
connection_manager = ConnectionManager()
message_handler = MessageHandler(game_manager, connection_manager)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "장부의 무게 API 서버",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


@app.websocket("/lobby/{game_id}")
async def lobby_websocket_endpoint(
    websocket: WebSocket,
    game_id: str,
    player: str = Query(..., description="플레이어 이름")
):
    """
    로비 WebSocket 엔드포인트
    
    플레이어 이름을 받아 서버에서 플레이어 ID를 자동 생성하고,
    연결과 동시에 게임에 자동 참가 처리합니다.
    
    Args:
        websocket: WebSocket 연결
        game_id: 게임 ID
        player: 플레이어 이름 (쿼리 파라미터)
    """
    # 플레이어 ID 자동 생성 (UUID)
    player_id = str(uuid.uuid4())
    
    # 연결 수락
    success = await connection_manager.connect(websocket, player_id)
    if not success:
        await websocket.close(code=1008, reason="최대 연결 수 초과")
        return
    
    try:
        # 연결 성공 메시지 전송 (플레이어 ID 포함)
        await connection_manager.send_personal_message(
            {
                "type": "CONNECTION_ESTABLISHED",
                "message": "로비에 연결되었습니다.",
                "player_id": player_id,
                "player_name": player,
                "game_id": game_id,
            },
            player_id,
        )
        
        # 자동 게임 참가 처리
        join_result = await message_handler.handle_join_game(
            player_id,
            {
                "type": "JOIN_GAME",
                "game_id": game_id,
                "player_name": player,
            }
        )
        
        # 참가 실패 시 에러 메시지 전송
        if not join_result.get("success"):
            await connection_manager.send_personal_message(
                {
                    "type": "ERROR",
                    "message": join_result.get("message", "게임 참가에 실패했습니다."),
                },
                player_id,
            )
            await websocket.close(code=1008, reason=join_result.get("message", "게임 참가 실패"))
            return
        
        # 메시지 수신 루프
        while True:
            try:
                # 메시지 수신
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 메시지 처리
                result = await message_handler.handle_message(player_id, message)
                
                # 결과 전송 (필요시)
                if result.get("success") is not None:
                    await connection_manager.send_personal_message(
                        {
                            "type": "ACTION_RESPONSE",
                            "data": result,
                        },
                        player_id,
                    )
            
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {
                        "type": "ERROR",
                        "message": "잘못된 JSON 형식입니다.",
                    },
                    player_id,
                )
            
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    
    finally:
        # 연결 해제
        connection_manager.disconnect(player_id)


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """
    WebSocket 엔드포인트 (기존 호환성 유지)
    
    Args:
        websocket: WebSocket 연결
        player_id: 플레이어 ID
    """
    # 연결 수락
    success = await connection_manager.connect(websocket, player_id)
    if not success:
        await websocket.close(code=1008, reason="최대 연결 수 초과")
        return
    
    try:
        # 연결 성공 메시지 전송
        await connection_manager.send_personal_message(
            {
                "type": "CONNECTION_ESTABLISHED",
                "message": "연결이 성공적으로 설정되었습니다.",
                "player_id": player_id,
            },
            player_id,
        )
        
        # 메시지 수신 루프
        while True:
            try:
                # 메시지 수신
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 메시지 처리
                result = await message_handler.handle_message(player_id, message)
                
                # 결과 전송 (필요시)
                if result.get("success") is not None:
                    await connection_manager.send_personal_message(
                        {
                            "type": "ACTION_RESPONSE",
                            "data": result,
                        },
                        player_id,
                    )
            
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {
                        "type": "ERROR",
                        "message": "잘못된 JSON 형식입니다.",
                    },
                    player_id,
                )
            
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    
    finally:
        # 연결 해제
        connection_manager.disconnect(player_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

