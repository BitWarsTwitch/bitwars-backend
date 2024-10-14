from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.endpoints.sockets import router as socket_router, socket_app
from app.endpoints.session import router as channel_session_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(socket_router, prefix="", tags=["Socket"])
app.include_router(channel_session_router, prefix="", tags=["Channel Sessions"])

app.mount("/", socket_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
