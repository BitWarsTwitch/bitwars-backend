import uuid
import socketio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.utils import compute_damage_based_on_attack_id
from models.channel_session import ChannelSessionModel

router = APIRouter()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)


async def _emit_attack(sio, attack_data, room):
    await sio.emit("attack", attack_data, room=room)


async def _emit_damage(sio, damage_amount, side, room):
    await sio.emit("damage", {"damage": damage_amount, "side": side}, room=room)


async def _get_sessions(db, sender_session_id):
    host_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == sender_session_id)
        .first()
    )

    if not host_session:
        return None, None, False

    friend_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == host_session.friend_code)
        .first()
    )

    is_friend_session = (
        friend_session and friend_session.friend_code == host_session.channel_id
    )

    return host_session, friend_session, is_friend_session


@router.post("/spawn_attack")
async def spawn_attack(
    sender_session_id: str,
    attack_id: int,
    user_name: str,
    db: Session = Depends(get_db),
):
    damage = compute_damage_based_on_attack_id(attack_id)
    host_session, friend_session, is_friend_session = await _get_sessions(
        db, sender_session_id
    )

    if not host_session:
        return {"message": "Session not found"}

    attack = {
        "id": str(uuid.uuid4()),
        "channel_id": host_session.channel_id,
        "attack_id": attack_id,
        "side": "left",
        "user_name": user_name,
        "damage": damage,
    }

    # emit host attack on A
    await _emit_attack(sio, attack, host_session.channel_id)

    if is_friend_session:
        # emit enemy attack on B
        attack.update({"side": "right", "channel_id": friend_session.channel_id})
        await _emit_attack(sio, attack, friend_session.channel_id)

    # Create background task for health updates
    async def update_health():
        await sio.sleep(5)
        async with db.begin():
            host_session.health += damage
            if is_friend_session:
                friend_session.health -= damage
            db.commit()

    # Schedule the background task
    sio.start_background_task(update_health)

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
    await sio.enter_room(sid, channel_id)
    db = SessionLocal()

    # Fetch current session from database
    session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == channel_id)
        .first()
    )

    # Initialize session data with database values
    session_data = {
        "leftName": session.name,
        "rightName": "Auto",
        "health": session.health if session else 50,
    }

    if session.friend_code:
        # Fetch friend session from database
        friend_session = (
            db.query(ChannelSessionModel)
            .filter(ChannelSessionModel.channel_id == session.friend_code)
            .first()
        )

        if friend_session:
            session_data["rightName"] = friend_session.name

    db.close()
    await sio.emit("initialize", session_data, to=sid)


@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
    # You may want to handle room leaving logic here if necessary
