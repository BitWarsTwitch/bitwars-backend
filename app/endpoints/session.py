from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from models.channel_session import ChannelSessionModel
from schemas.channel_session import ChannelSession as ChannelSessionSchema
from schemas.channel_session import ChannelSessionCreate

router = APIRouter()


@router.get("/sessions", response_model=List[ChannelSessionSchema])
def get_all_channel_sessions(db: Session = Depends(get_db)):
    channel_sessions = db.query(ChannelSessionModel).all()
    return channel_sessions


@router.post("/sessions", response_model=ChannelSessionSchema)
def create_channel_session(
    session: ChannelSessionCreate, db: Session = Depends(get_db)
):
    db_session = ChannelSessionModel(
        channel_id=session.channel_id,
        friend_code=session.friend_code,
        total_health=session.total_health,
        current_bit_count=session.current_bit_count,
    )
    db.add(db_session)
    db.commit()

    return db_session


@router.put("/sessions/{channel_id}", response_model=ChannelSessionSchema)
def update_channel_session(
    channel_id: str, session: ChannelSessionCreate, db: Session = Depends(get_db)
):
    db_session = (
        db.query(ChannelSessionModel)
        .filter(ChannelSessionModel.channel_id == channel_id)
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.friend_code = session.friend_code
    db_session.total_health = session.total_health
    db_session.current_bit_count = session.current_bit_count

    db.commit()
    db.refresh(db_session)
    return db_session
