import socketio
from fastapi import APIRouter

router = APIRouter()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

# In-memory storage for squares
squares = []


@router.post("/spawn_square")
async def spawn_square():
    square = {"id": len(squares), "position": "bottom-left"}
    squares.append(square)
    await sio.emit("new_square", [square])
    return {"message": "Square spawned"}


@sio.event
async def connect(sid, environment):
    print("Client connected:", sid)
    # await sio.emit("new_square", squares, room=sid)


@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
