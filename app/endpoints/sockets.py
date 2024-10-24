import uuid
import socketio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils import compute_damage_based_on_attack_id
from models.channel_session import ChannelSessionModel

router = APIRouter()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)


@router.post("/spawn_attack")
async def spawn_attack(
    sender_session_id: str,
    attack_id: int,
    user_name: str,
    db: Session = Depends(get_db),
):
    damage = compute_damage_based_on_attack_id(attack_id)
    host_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == sender_session_id)
        .first()
    )

    if not host_session:
        return {"message": "Session not found"}

    friend_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == host_session.friend_code)
        .first()
    )

    is_friend_session = (
        friend_session and friend_session.friend_code == host_session.channel_id
    )

    # emit host attack on A
    attack = {
        "id": str(uuid.uuid4()),
        "channel_id": host_session.channel_id,
        "attack_id": attack_id,
        "side": "left",
        "user_name": user_name,
    }
    await sio.emit("attack", attack, room=host_session.channel_id)

    if is_friend_session:
        # emit enemy attack on B
        attack.update({"side": "right", "channel_id": friend_session.channel_id})
        await sio.emit("attack", attack, room=host_session.channel_id)

    # 5 seconds later emit enemy damage on A
    await sio.sleep(5)
    await sio.emit(
        "damage", {"damage": damage, "side": "right"}, room=host_session.channel_id
    )

    if is_friend_session:
        # emit host damage on B
        await sio.emit(
            "damage", {"damage": damage, "side": "left"}, room=friend_session.channel_id
        )

    return {"message": "Attack created with ID: {} was successful".format(attack["id"])}


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
