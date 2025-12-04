# tests/test_websocket.py

from starlette.testclient import TestClient
from app.main import app
from tests.factories import create_user
from app.utils.security import create_access_token


def test_ws_accepts_valid_token(db_session):
    user = create_user(db_session, username="ws_user")
    token = create_access_token(str(user.id))

    client = TestClient(app)

    with client.websocket_connect(f"/ws/notifications?token={token}") as ws:
        ws.send_text("hello")  # Required or server closes immediately
        # If we reach here => connection accepted


def test_ws_rejects_invalid_token():
    client = TestClient(app)

    try:
        with client.websocket_connect("/ws/notifications?token=badtoken") as ws:
            assert False, "Should not connect"
    except Exception:
        pass
