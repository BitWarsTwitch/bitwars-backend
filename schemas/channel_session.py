from pydantic import BaseModel


class ChannelSessionBase(BaseModel):
    channel_id: str
    friend_code: str
    total_health: int
    current_bit_count: int


class ChannelSessionCreate(ChannelSessionBase):
    pass


class ChannelSession(ChannelSessionBase):
    id: int

    class Config:
        orm_mode = True
