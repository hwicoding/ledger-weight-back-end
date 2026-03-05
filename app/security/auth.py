from typing import Optional


def get_player_id_from_token(token: Optional[str]) -> Optional[str]:
    """
    WebSocket 인증 토큰에서 플레이어 ID를 추출합니다.

    임시: 토큰 문자열을 그대로 플레이어 ID로 사용합니다.
    JWT 검증 도입 전까지 이 동작을 사용하며, 이후 JWT payload에서
    player_id(또는 sub) 추출 로직으로 교체할 예정입니다.

    Args:
        token: 인증 토큰 문자열 (예: JWT)

    Returns:
        유효한 경우 플레이어 ID, 그렇지 않으면 None
    """
    if token is None:
        return None

    token = token.strip()
    if not token:
        return None

    # TODO: JWT 기반 토큰 검증 및 player_id 추출 로직으로 교체
    # 예: payload = jwt.decode(token, ...); return payload.get("sub")
    # 현재는 토큰 문자열을 그대로 player_id로 사용 (임시)
    return token

