import httpx
import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()
TWITCH_JWK_URL = "https://id.twitch.tv/oauth2/keys"


async def fetch_public_key():
    async with httpx.AsyncClient() as client:
        response = await client.get(TWITCH_JWK_URL)
        jwks = response.json()["keys"]
        return {key["kid"]: key for key in jwks}  # Caches JWK by Key ID (kid)


async def verify_jwt(token: str = Security(security), jwks=Depends(fetch_public_key)):
    try:
        # Decode the token with the cached JWKs
        kid = jwt.get_unverified_header(token.credentials)["kid"]
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwks[kid])
        decoded = jwt.decode(
            token.credentials,
            public_key,
            algorithms=["RS256"],
            audience="YOUR_CLIENT_ID",
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
