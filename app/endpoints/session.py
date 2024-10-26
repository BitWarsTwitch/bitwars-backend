from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.auth import auth_scheme, verify_and_decode_jwt
from app.core.database import get_db
from models.channel_session import ChannelSessionModel
from schemas.channel_session import ChannelSession as ChannelSessionSchema
from schemas.channel_session import ChannelSessionCreate

router = APIRouter()


@router.get("/sessions", response_model=List[ChannelSessionSchema])
def get_all_channel_sessions(db: Session = Depends(get_db)):
    channel_sessions = db.query(ChannelSessionModel).all()
    return channel_sessions


@router.get("/sessions/{channel_id}", response_model=ChannelSessionSchema)
def get_channel_session(
    channel_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(auth_scheme),
):
    # Extract token from Authorization header
    jwt_token = token.credentials
    verify_and_decode_jwt(jwt_token)

    db_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == channel_id)
        .first()
    )
    if not db_session:
        # Create new session with default health of 50
        db_session = ChannelSessionModel(channel_id=channel_id, health=50)
        db.add(db_session)
        db.commit()

    return db_session


@router.post("/sessions", response_model=ChannelSessionSchema)
def create_channel_session(
    session: ChannelSessionCreate,
    db: Session = Depends(get_db),
    token: str = Depends(auth_scheme),
):
    jwt_token = token.credentials
    verify_and_decode_jwt(jwt_token)

    db_session = ChannelSessionModel(
        channel_id=session.channel_id,
        friend_code=session.friend_code,
        heath=session.health,
        name=session.name,
        enemy_name=session.enemy_name,
    )
    db.add(db_session)
    db.commit()

    return db_session


@router.put("/sessions/{channel_id}", response_model=ChannelSessionSchema)
def update_channel_session(
    channel_id: str,
    session: ChannelSessionCreate,
    db: Session = Depends(get_db),
    token: str = Depends(auth_scheme),
):
    jwt_token = token.credentials
    verify_and_decode_jwt(jwt_token)

    db_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == channel_id)
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.friend_code = session.friend_code
    db_session.health = session.health
    db_session.name = session.name
    db_session.enemy_name = session.enemy_name

    print(db_session.__dict__)
    print(session.__dict__)

    db.commit()
    db.refresh(db_session)
    return db_session
