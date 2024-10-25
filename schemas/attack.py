from pydantic import BaseModel


class AttackPayload(BaseModel):
    sender_session_id: str
    attack_id: int
    user_name: str
