import uuid
import socketio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from models.channel_session import ChannelSessionModel

router = APIRouter()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)


@router.post("/spawn_attack")
async def spawn_attack(
    sender_session_id: str,
    attack_id: int,
    damage: int,
    user_name: str,
    db: Session = Depends(get_db),
):
    attack = {
        "id": str(uuid.uuid4()),
        "channel_id": sender_session_id,
        "attack_id": attack_id,
        "damage": damage,
        "user_name": user_name,
    }
    # Emit the attack event to the specific room identified by sender_session_id
    await sio.emit("test", room=sender_session_id)
    await sio.emit("attack", attack, room=sender_session_id)
    return {"message": "Attack created with ID: {}".format(sender_session_id)}


@router.post("/damage_session")
async def damage_session(
    channel_id: str,
    bit_count: int,
    db: Session = Depends(get_db),
):
    current_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == channel_id)
        .first()
    )


@sio.event
async def connect(sid, env):
    print("Client connected:", sid)

    # Assuming the client sends the channel_id as a query parameter
    query_string = env.get("QUERY_STRING", "")
    channel_id = (
        query_string.split("channel=")[1].split("&")[0]
        if "channel=" in query_string
        else ""
    )
    print("Room:", channel_id)
    await sio.enter_room(sid, channel_id)


@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
    # You may want to handle room leaving logic here if necessary
