from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from models.channel_session import ChannelSessionModel
from schemas.channel_session import ChannelSession as ChannelSessionSchema


router = APIRouter()


@router.get("/sessions", response_model=List[ChannelSessionSchema])
def get_all_channel_sessions(db: Session = Depends(get_db)):
    channel_sessions = db.query(ChannelSessionModel).all()
    return channel_sessions
