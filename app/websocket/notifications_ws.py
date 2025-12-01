from typing import Dict,List
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.utils.security import decode_access_token
from app.models.user import User

router=APIRouter(prefix='/ws',tags=['WebSockets'])

class ConnectionManager:
    def __init__(self)->None:
        self.active_connections:Dict[int,List[WebSocket]]={}


    async def connect(self,user_id:int,websocket:WebSocket)->None:
        await websocket.accept()
        self.active_connections.setdefault(user_id,[]).append(websocket)

    def disconnect(self,user_id:int,websocket:WebSocket):
        conns=self.active_connections.get(user_id)
        if not conns:
            return
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self.active_connections.pop(user_id,None)


    async def send_personal_json(self,user_id:int,data:dict)->None:
        conns=self.active_connections.get(user_id,[])
        for ws in list(conns):
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(user_id,ws)


manager=ConnectionManager()


@router.websocket('/notifications')
async def notifications_ws(websocket:WebSocket):
     """
    Client connects with:
      ws://127.0.0.1:8000/ws/notifications?token=JWT_TOKEN_HERE
    """
     token=websocket.query_params.get('token')
     if not token:
         await websocket.close(code=1008)
         return
     

     try:
         payload=decode_access_token(token)
         user_id=int(payload.get('sub'))

     except Exception:
         await websocket.close(code=1008)
         return
     db:Session=SessionLocal()

     try:
         user=db.query(User).filter(User.id==user_id).first()
         if not user:
             await websocket.close(code=1008)
             return
     finally:
         db.close()
     await manager.connect(user_id, websocket)

     try:
        # Just keep the connection open; ignore any incoming messages
        while True:
            await websocket.receive_text()
     except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
