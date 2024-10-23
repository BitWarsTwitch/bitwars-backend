from sqlalchemy import Column, Integer, String
from app.core.database import Base


class ChannelSessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(255), primary_key=True)
    friend_code = Column(String)
    total_health = Column(Integer)
    current_bit_count = Column(Integer)
