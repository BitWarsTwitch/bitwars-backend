import os
import base64
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
import jwt

load_dotenv()
auth_scheme = HTTPBearer()

TWITCH_JWK_URL = "https://id.twitch.tv/oauth2/keys"


twitch_ext_secret = base64.b64decode(os.getenv("TWITCH_EXT_SECRET"))


def verify_and_decode_jwt(token: str):
    try:
        # Decode the token using the secret and HS256 algorithm
        payload = jwt.decode(token, twitch_ext_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
